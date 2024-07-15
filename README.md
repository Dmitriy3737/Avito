# Микросервис для работы с балансом пользователей

## Описание
Этот микросервис предоставляет API для работы с балансом пользователей, включая зачисление средств, списание средств, перевод средств от пользователя к пользователю, а также метод получения баланса пользователя. Сервис предоставляет HTTP API и принимает/отдает запросы/ответы в формате JSON.

## Установка

### Требования
- *Docker и Docker Compose*

### Шаги для установки

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. Запустите сервис с использованием Docker Compose:
    ```bash
    docker-compose up --build
    ```

3. Настройте базу данных PostgreSQL и примените миграции:
    ```bash
    docker-compose exec django python manage.py migrate
    ```

4. Запустите сервер:
    ```bash
    docker-compose exec django python manage.py runserver 0.0.0.0:8000
    ```
## Примеры использования API (с аутентификацией JWT)
1. Получение токена аутентификации
- Postman запрос:

    - Метод: POST
    - URL: http://localhost:8000/api/token/
    - Headers:
        - Content-Type: application/json
    - Body (raw, JSON):

```json
{
    "username": "your_username",
    "password": "your_password"
}
```
- Ответ:
```json
{
    "access": "your_access_token",
    "refresh": "your_refresh_token"
}
```

2. Использование токена для аутентификации

Во всех последующих запросах необходимо добавить заголовок 
 - Authorization: Bearer your_access_token.

3. Зачисление средств на баланс
- Postman запрос:

    - Метод: POST
    - URL: http://localhost:8000/api/add_funds/
    - Headers:
        - Content-Type: application/json
        - Authorization: Bearer your_access_token
    - Body (raw, JSON):
```json
{
    "user_id": 1,
    "amount": 100
}
```
- Ответ:
```json
{
    "id": 71,
    "user": 2,
    "amount": "10.00",
    "transaction_type": "deposit",
    "created_at": "2024-07-11T22:01:15.242010+03:00",
    "user_id": 2
}
```

4. Резервирование средств на отдельном счете
- Postman запрос:

    - Метод: POST
    - URL: http://localhost:8000/api/reserve_funds/
    - Headers:
        - Content-Type: application/json
        - Authorization: Bearer your_access_token
    - Body (raw, JSON):
```json
{
    "user_id": 2,
    "service_id": 101,
    "order_id": 1001,
    "amount": 50
}
```
- Ответ:
```json
{
    "id": 72,
    "user": 2,
    "amount": "1.00",
    "transaction_type": "reservation",
    "created_at": "2024-07-11T22:20:54.716534+03:00",
    "user_id": 2
}
```
5. Признание выручки (списание из резерва)
- Postman запрос:

    - Метод: POST
    - URL: http://localhost:8000/api/deduct_funds/
    - Headers:
        - Content-Type: application/json
        - Authorization: Bearer your_access_token
    - Body (raw, JSON):
```json
{
    "user_id": 2,
    "service_id": 876,
    "order_id": 432,
    "amount": 1.00
}
```
- Ответ:
```json
{
    "id": 73,
    "user": 2,
    "amount": "1.00",
    "transaction_type": "revenue_recognition",
    "created_at": "2024-07-11T22:25:15.070301+03:00",
    "user_id": 2
}
```
6. Перевод средств от одного пользователя к другому
- Postman запрос:

    - Метод: POST
    - URL: http://localhost:8000/api/transfer_funds/
    - Headers:
        - Content-Type: application/json
        - Authorization: Bearer your_access_token
    - Body (raw, JSON):
```json
{
    "sender_id": 4,
    "recipient_id": 2,
    "amount": 99.00
}
```
- Ответ:
```json
{
    "sender_transaction": {
        "id": 74,
        "user": 4,
        "amount": "-100.00",
        "transaction_type": "transfer",
        "created_at": "2024-07-11T22:38:03.444277+03:00",
        "user_id": 4
    },
    "recipient_transaction": {
        "id": 75,
        "user": 2,
        "amount": "100.00",
        "transaction_type": "transfer",
        "created_at": "2024-07-11T22:38:03.444964+03:00",
        "user_id": 2
    }
}
```
7. Получение баланса пользователя
- Postman запрос:

    - Метод: GET
    - URL: http://localhost:8000/api/balances/
    - Headers:
        - Content-Type: application/json
        - Authorization: Bearer your_access_token
    - Параметры запроса (Query Parameters):
        - user_id: идентификатор пользователя, баланс которого нужно получить

Пример запроса:

    URL: http://localhost:8000/api/balances/?user_id=2

- Ответ:
```json
{
    "user_id": 2,
    "amount": 100
}
```


## Архитектура и структура проекта

#### Проект состоит из следующих основных компонентов:

`models.py`: Определяет модели базы данных.
`views.py`: Содержит обработчики для каждого API-метода.
`urls.py`: Маршрутизация URL к соответствующим представлениям.
`serializers.py`: Определяет сериализаторы для преобразования данных между форматами JSON и моделями.
`Dockerfile` и `docker-compose.yml`: Файлы для настройки контейнеров Docker.

## Вопросы и решения
#### Вопросы, с которыми столкнулся:

1. Как организовать транзакции для перевода средств между пользователями? 
    - Решение: Использование транзакций базы данных для обеспечения атомарности операций.

2. Как обрабатывать ошибки при недостаточном балансе?
    - Решение: Валидация и возврат соответствующих сообщений об ошибках.

## Полезные ссылки

- [Начало работы с Docker](https://www.docker.com/get-started)
- [Документация Docker Compose](https://docs.docker.com/compose/)
- [Официальный сайт Django](https://www.djangoproject.com/start/)
- [Быстрый старт DRF](https://www.django-rest-framework.org/tutorial/quickstart/)
- [Документация PostgreSQL](https://www.postgresql.org/docs/)
- [Введение в JWT](https://jwt.io/introduction/)
- [Руководство по Postman](https://learning.postman.com/docs/getting-started/introduction/)

## Контакты

*Если у вас есть вопросы или предложения, пожалуйста, свяжитесь со мной:*

- `Email:` decl37@bk.ru 
- `GitHub:` Dmitriy3737

