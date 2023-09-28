# Bill Checking and Payment Bot

## Описание

Этот бот предназначен для автоматической проверки и оплаты счетов через различные сервисы, такие как МосОблЕИРЦ, Мос.ру и МГТС. Бот также предоставляет возможность передачи показаний счетчиков воды и электричества.

## Основные функции

1. Автоматическая проверка счетов в заданные дни и время.
2. Отправка уведомлений о найденных счетах с возможностью оплаты прямо из уведомления.
3. Возможность передачи показаний счетчиков воды и электричества.
4. Логирование всех действий и ошибок.

## Начало работы

1. Установите все необходимые зависимости из файла `requirements.txt` (если он есть).
2. Убедитесь, что у вас есть файл `config.py` с необходимыми настройками, такими как API_TOKEN.
3. Запустите бота, выполнив команду: `python your_bot_filename.py`.

## Команды бота

- `/start`: Запускает бота и показывает главное меню.
- `Проверить счета`: Проверяет все доступные счета и показывает их статус.
- `Вода`: Начинает процесс передачи показаний счетчика воды.
- `Электричество`: Начинает процесс передачи показаний счетчика электричества.
- `Передать показания`: Показывает меню для выбора типа показаний для передачи.
- `Меню`: Возвращает вас в главное меню.

## Планирование задач

Бот использует планировщик задач для автоматической проверки счетов и отправки уведомлений о передаче показаний. По умолчанию задачи запланированы на определенные дни и время, но вы можете настроить их в соответствии с вашими потребностями.

## Логирование

Все действия и ошибки бота записываются в файл `logs/info.log`. Это помогает отслеживать все действия бота и быстро находить и устранять возникающие проблемы.

---
## Description
This bot is designed for automatic bill checking and payment through various services such as MosOblEIRC, Mos.ru, and MGTS. The bot also offers the ability to submit water and electricity meter readings.

## Main Features
- Automatic bill checking on specified days and times.
- Sending notifications about found bills with the option to pay directly from the notification.
- Ability to submit readings from water and electricity meters.
- Logging of all actions and errors.

## Getting Started
1. Install all necessary dependencies from the `requirements.txt` file (if available).
2. Ensure you have the `config.py` file with the required settings, such as API_TOKEN.
3. Launch the bot by executing the command: `python your_bot_filename.py`.

## Bot Commands
- `/start`: Initiates the bot and displays the main menu.
- `Check Bills`: Checks all available bills and displays their status.
- `Water`: Starts the process of submitting water meter readings.
- `Electricity`: Begins the process of submitting electricity meter readings.
- `Submit Readings`: Displays a menu to choose the type of readings to submit.
- `Menu`: Returns you to the main menu.

## Task Scheduling
The bot uses a task scheduler for automatic bill checks and sending reading submission reminders. By default, tasks are scheduled for specific days and times, but you can adjust them according to your needs.

## Logging
All bot actions and errors are logged in the `logs/info.log` file. This helps in tracking all bot activities and quickly identifying and resolving any issues.

---