# Тестовое задание

## Запуск приложения

Для запуска необходимо создать виртуальное окружение и активировать его.
После этого необходимо ввести в терминал: *pip install -r requirements.txt*.
После установки всех необходимый библиотек, можно запускать *main.py*

### Этапы выполняемые main.py
-> Отправка в терминал команды для сборки докер контейнера, в котором лежит postgresql.<br>
-> Ожидание 10 секунд. (Примерное необходимое время для сборки и инициализации этого контейнера)<br>
-> Отправка в терминал команды для запуска миграции alembic<br>
-> Запуск двух разных терминалах, сервера сайта и микросервиса, который взаимодействует с Azure DevOps API<br>

## Описание микросервисов

### Сервер FastApi

-> Отправка списка всех пользователей, у которых есть задачи в Azure DevOps. <br>
-> Отправка всех достижений и задач этого человека <br>

### Микросервис для взаимодействия с Azure DevOps

-> Каждые 10 минут делать запрос на *https://dev.azure.com/{organization}/{project}/_apis/wit/reporting/workitemrevisions*
-> Распарсивает все Work Item которые были получены и добавляет/обновляет все Work Items, которые есть в таблице Tasks