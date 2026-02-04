import time
import os
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from bpmn.element_factories import DiagramFactory
from api.services import (
    predict_service as ps,
    ocr_service as os,
    convert_service as cs,
    storage_service as ss,
)
from commons.utils import sample_bpmn, here


async def convert_image(request: Request):
    """Обрабатывает POST-запрос на конвертацию изображения в BPMN-модель."""

    try:
        form = await request.form()
        file = form.get('image')

        # Валидация наличия файла
        if file is None:
            return JSONResponse(
                content={"error": "Файл 'image' не найден в запросе"},
                status_code=400
            )

        # Валидация имени файла
        if not file.filename:
            return JSONResponse(
                content={"error": "Имя файла отсутствует"},
                status_code=400
            )

        t = int(time.time_ns())
        path = here("../../temp_files/img_{}_{}".format(t, file.filename))
        with open(path, 'wb+') as disk_file:
            disk_file.write(await file.read())
        ocr_img, predict_img = ss.get_ocr_and_predict_images(path)

        if ocr_img is None or predict_img is None:
            return PlainTextResponse(content=sample_bpmn, status_code=200)

        if "elements" in form and form["elements"] == 'true':
            obj_predictions = ps.predict_object(predict_img)
            elements = cs.convert_object_predictions(obj_predictions)

            if "flows" in form and form["flows"] == 'true':
                kp_predictions = ps.predict_keypoint(ocr_img)
                flows = cs.convert_keypoint_prediction(kp_predictions)
                cs.link_flows(flows, elements)
                elements.extend(flows)

            if "ocr" in form and form["ocr"] == 'true':
                text = os.get_text_from_img(ocr_img)
                os.link_text(text, elements)

            bpmn_diagram = DiagramFactory.create_element(elements)
            rendered_bpmn_model = cs.render_diagram(bpmn_diagram)
        else:
            rendered_bpmn_model = sample_bpmn

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
