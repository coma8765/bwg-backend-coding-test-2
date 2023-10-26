# Сервис для мониторинга текущего курса обмена

_Сделал [Ananev Nikita](https://t.me/coma8765)_

> Решение второй тестовой задачи от BWG,
> согласно [техническому заданию](docs/TASK.md)

## Использование

## Intro
_[Конфигурация](./docker-compose.yml) состоит из proxy, RabbitMQ, 
API service, exchange monitor service.  API определён как 4 реплики. 
Поставлены ограничения на использования ресурсов исходя 
из [нагрузочного тестирования](./docs/LOAD_TESTING.md)_

### Переменное окружение

> Воспользуйтесь _dotenv_ (для Docker `.env.docker`), либо средства Докер для
> указания переменных


- **RABBITMQ_URI** — RabbitMQ's connection string
- **APP_URI** — Application uri for testing
- **BINANCE_API_KEY** & **BINANCE_API_SECRET** — Auth for Binance

### Docker Compose

_Скопируйте [`.env.example`](.env.example) в `.env.docker` и заполните его._

```shell
docker compose up -d  # Equal "make up" 
```

## Техническое описание

### Архитектура

> Архитектура придерживается методологии чистой архитектуры.
> Внешние взаимодействия описаны в [адаптерах](./src/adapters).
> Бизнес логика описана в [модулях](./src/modules),
> а именно в [первом](./src/modules/api) и 
> [втором](./src/modules/exchange_monitor).

### Библиотеки

[//]: # (TODO: @coma8765 add production libraries)

##### Библиотеки для разработки

* **mypy** — проверка типов
* **black** — форматер кода
* **pylint** — линтинг кода
* **isort** — сортировщик импортов
* **locust** — нагрузочное тестирование

## Тестирование

[Нагрузочное тут](./docs/LOAD_TESTING.md)

### Code quality

_Команда: `make pretty`_

#### Pylint

```text
>> pylint src
--------------------------------------------------------------------
Your code has been rated at 9.63/10 (previous run: 10.00/10, +0.0)
```

#### Black

```text
>> black src
All done! ✨ 🍰 ✨
43 files left unchanged.
```

#### Mypy

```text
>> mypy src
Success: no issues found in 43 source files
```
