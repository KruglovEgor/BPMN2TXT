# BPMN2TXT

## Быстрый старт (сборка всех сервисов и запуск (llm на GPU))

```bash
docker compose --profile gpu up --build gateway llm-gpu ui pipeline
```

## Запуск через Docker Compose

В корневом [docker-compose.yml](docker-compose.yml) объявлены все сервисы.

### Pipeline proccesing

**Сборка образа:**
```bash
docker compose build pipeline
```

**Запуск:**
```bash
docker compose up pipeline
```

**Сборка + запуск:**
```bash
docker compose up --build pipeline
```

Pipeline proccesing будет доступен на `http://localhost:5000`

### LLM (llama.cpp server)

#### CPU версия

**Сборка образов:**
```bash
docker compose --profile cpu build model-init llm-cpu
```

**Запуск:**
```bash
docker compose --profile cpu up model-init llm-cpu
```

**Сборка + запуск:**
```bash
docker compose --profile cpu up --build model-init llm-cpu
```

#### GPU версия

**Сборка образов:**
```bash
docker compose --profile gpu build model-init llm-gpu
```

**Запуск:**
```bash
docker compose --profile gpu up model-init llm-gpu
```

**Сборка + запуск:**
```bash
docker compose --profile gpu up --build model-init llm-gpu
```

**Переменные окружения:**
Переменные (MODEL_PATH, HF_MODEL_URL, порты, ctx и т.д.) лежат в корневом `.env`.
