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
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем detectron2
RUN pip install --no-cache-dir git+https://github.com/facebookresearch/detectron2.git@v0.6

# Фиксируем версии библиотек совместимые с torch 1.10 и detectron2 v0.6
RUN pip install --no-cache-dir "numpy==1.23.5" "Pillow==9.5.0"

# Копируем код приложения
COPY . .

# Порт приложения
EXPOSE 5000

# Запуск
CMD ["python", "app.py"]
