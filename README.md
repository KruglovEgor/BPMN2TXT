# BPMN2TXT

## Запуск через Docker Compose

В корневом [docker-compose.yml](docker-compose.yml) объявлены все сервисы.

### Backend (pipeline)

- Запуск:
	- `docker compose up --build backend`
- Backend будет доступен на `http://localhost:5000`

### LLM (llama.cpp server)

Включается профилями:

- CPU:
	- `docker compose --profile cpu up --build model-init llm-cpu`
- GPU:
	- `docker compose --profile gpu up --build model-init llm-gpu`

Переменные (MODEL_PATH, HF_MODEL_URL, порты, ctx и т.д.) лежат в корневом `.env`.
