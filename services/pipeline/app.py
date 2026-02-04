from commons.utils import here
from api.resources.convert_resource import convert_image
from fastapi.responses import PlainTextResponse
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn
import os
import sys
sys.path.append('.')


def create_app():
    app = FastAPI(debug=False)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*']
    )

    app.post(
        '/api/v1/convert',
        summary='Конвертация изображения в BPMN',
        description='Принимает изображение и возвращает BPMN в формате XML.',
        response_class=PlainTextResponse
    )(convert_image)

    static_files_folder = here("static")
    if os.path.exists(static_files_folder) and os.path.isdir(static_files_folder):
        app.mount('/', StaticFiles(directory=static_files_folder, html=True))

    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host='0.0.0.0', port=int(
        os.environ.get("BACKEND_PORT", "5000")))
