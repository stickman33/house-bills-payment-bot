from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Проверить счета"),
            KeyboardButton("Передать показания")
        ]
    ],
    resize_keyboard=True
)

sub_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Меню"),
            KeyboardButton("Передать показания")
        ]
    ],
    resize_keyboard=True,
)

meter_readings = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton("Электричество"),
            KeyboardButton("Вода")
        ],
        [
            KeyboardButton("Меню")
        ]
    ],
    resize_keyboard=True
)


