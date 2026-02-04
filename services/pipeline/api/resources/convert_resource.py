import time
import asyncio
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile, File
from starlette.responses import PlainTextResponse, JSONResponse
from bpmn.element_factories import DiagramFactory
from api.services import (
    predict_service as ps,
    ocr_service as ocr,
    convert_service as cs,
    storage_service as ss,
)
from commons.utils import sample_bpmn, here

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Thread pool для параллельного выполнения моделей
executor = ThreadPoolExecutor(max_workers=3)

# Допустимые форматы изображений
ALLOWED_EXTENSIONS = {'.png', '.jpg',
                      '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}


async def convert_image(image: UploadFile = File(...)):
    """Обрабатывает POST-запрос на конвертацию изображения в BPMN-модель.

    Пайплайн выполняется с параллельным запуском всех моделей.
    """

    try:
        if image is None or not image.filename:
            return JSONResponse(
                content={"error": "Имя файла отсутствует"},
                status_code=400
            )

        # Валидация формата файла
        file_ext = image.filename.lower().split(
            '.')[-1] if '.' in image.filename else ''
        if f'.{file_ext}' not in ALLOWED_EXTENSIONS:
            return JSONResponse(
                content={
                    "error": f"Недопустимый формат файла. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                },
                status_code=400
            )

        safe_filename = f"{int(time.time_ns())}.{file_ext}"
        path = here(f"../../tmp/{safe_filename}")

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb+') as disk_file:
            disk_file.write(await image.read())
        ocr_img, predict_img = ss.get_ocr_and_predict_images(path)

        if ocr_img is None or predict_img is None:
            return PlainTextResponse(content=sample_bpmn, status_code=200)

        # Параллельный запуск всех моделей
        loop = asyncio.get_event_loop()

        obj_predictions_future = loop.run_in_executor(
            executor, ps.predict_object, predict_img
        )
        kp_predictions_future = loop.run_in_executor(
            executor, ps.predict_keypoint, ocr_img
        )
        text_future = loop.run_in_executor(
            executor, ocr.get_text_from_img, ocr_img
        )

        # Ожидаем завершения всех моделей
        obj_predictions, kp_predictions, text = await asyncio.gather(
            obj_predictions_future,
            kp_predictions_future,
            text_future
        )

        # Последовательная обработка результатов
        elements = cs.convert_object_predictions(obj_predictions)
        flows = cs.convert_keypoint_prediction(kp_predictions)
        cs.link_flows(flows, elements)
        elements.extend(flows)
        ocr.link_text(text, elements)

        bpmn_diagram = DiagramFactory.create_element(elements)
        rendered_bpmn_model = cs.render_diagram(bpmn_diagram)

        return PlainTextResponse(content=rendered_bpmn_model, status_code=200)

    except ValueError as e:
        return JSONResponse(
            content={"error": f"Ошибка значения: {str(e)}"},
            status_code=400
        )
    except FileNotFoundError as e:
        return JSONResponse(
            content={"error": f"Ошибка при работе с файлом: {str(e)}"},
            status_code=500
        )
    except Exception as e:
        return JSONResponse(
            content={"error": f"Внутренняя ошибка сервера: {str(e)}"},
            status_code=500
        )
