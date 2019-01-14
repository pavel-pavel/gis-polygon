

# Установка #
1. Открыть директорию gis-polygon (с poetry.lock)
2. Установить python 3.7 и poetry
3. `poetry install` (установит зависимости)
4. Настроить переменные окружения в файле `.env` (инициализировать копией `.defaultenv`)
5. `poetry run python -m gis_polygon.manage db upgrade` (применить миграции)
6. Запустить `poetry run python -m gis_polygon.manage run`

## Запуск тестов ##
1. Настроить переменные окружения в файле `.testenv` (инициализировать копией `.defaultenv`)
2. Запустить `poetry run pytest tests`


## Коллекция запросов для REST-клиентов ##
https://www.getpostman.com/collections/0926d5b57762f9ef8d70