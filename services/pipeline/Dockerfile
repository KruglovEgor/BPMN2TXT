# syntax=docker/dockerfile:1.7
FROM python:3.9-slim-bullseye

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    tesseract-ocr \
    tesseract-ocr-rus \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Устанавливаем detectron2
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install git+https://github.com/facebookresearch/detectron2.git@v0.6

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
