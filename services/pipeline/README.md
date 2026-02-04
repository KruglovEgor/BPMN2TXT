# BPMN2TXT (pipeline processing backend)

"Этот раздел содержит код сервиса для распознавания изображений BPMN диаграмм и преобразования в BPMN код.

## Запуск в Docker

Из папки [backend](./):

1. Соберите контейнер:

   ```bash
   docker-compose build
   ```

2. Запустите контейнер:
   ```bash
   docker-compose up
   ```
3. Приложение будет доступно по адресу `http://localhost:5000`

Для остановки контейнера:

```bash
docker-compose down
```
