import logging
from datetime import datetime, time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from pytz import timezone

import config
from keyboards.choice_buttons import *
from services import mosobleirc, mosru, mgts, mosru_water_meter, mosru_electricity_meter

logging.basicConfig(level=logging.DEBUG)
logger.add("logs/info.log", level="DEBUG", rotation="20 MB", compression="tar.gz")


bot = Bot(token=config.API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


zero_cost_count = 0
check_logs_count = 0
payment_bills_dict = dict()


begin_maintenance = time(23, 00)
end_maintenance = time(7, 00)


async def check_mosobleirc():
    cost, payment_url = mosobleirc.run(logger)
    global zero_cost_count, check_logs_count

    if mosobleirc.mosobleirc_check_logs:
        check_logs_count += 1
        await bot.send_message(chat_id=11279097, text="Ошибка доступа к МосОблЕИРЦ, проверьте логи", parse_mode="html")
    elif cost == 0:
        zero_cost_count += 1
    else:
        button_pay_mosobleirc = InlineKeyboardButton("💸 Оплатить", url=payment_url)
        keyboard_mosobleirc = InlineKeyboardMarkup(row_width=1).add(button_pay_mosobleirc)
        payment_bills_dict[f"<b>МосОблЕИРЦ</b> \nК оплате: {str(cost)}"] = keyboard_mosobleirc


async def check_mosru():
    cost_dict, payment_url = mosru.run(logger)
    global zero_cost_count, check_logs_count

    if mosru.mosru_check_logs:
        check_logs_count += 1
        await bot.send_message(chat_id=11279097, text="Ошибка доступа к Мос.ру, проверьте логи", parse_mode="html")

    for operator, cost in cost_dict.items():
        if cost == 0:
            zero_cost_count += 1
        else:
            button_pay_mosru = InlineKeyboardButton("💸 Оплатить", url=payment_url)
            keyboard_mosru = InlineKeyboardMarkup(row_width=1).add(button_pay_mosru)
            payment_bills_dict[f"<b>Мос.ру</b> \n<b>{operator}</b>\nК оплате: {str(cost)}"] = keyboard_mosru


async def check_mgts():
    cost, payment_url = mgts.run(logger)
    global zero_cost_count, check_logs_count

    if mgts.mgts_check_logs:
        check_logs_count += 1
        await bot.send_message(chat_id=11279097, text="Ошибка доступа к МГТС, проверьте логи", parse_mode="html")
    elif cost == 0:
        zero_cost_count += 1
    else:
        button_pay_mgts = InlineKeyboardButton("💸 Оплатить", url=payment_url)
        keyboard_mgts = InlineKeyboardMarkup(row_width=1).add(button_pay_mgts)
        payment_bills_dict[f"<b>МГТС</b> \nК оплате: {str(cost)}"] = keyboard_mgts


# @dp.message_handler(commands=["start"])
# async def send_welcome(message: types.Message):
#     await message.reply("Привет!")

@dp.message_handler(text=["Проверить счета"], user_id=11279097)
async def check_bills(message: types.Message):
    global zero_cost_count, check_logs_count
    current_time = datetime.now(timezone('Europe/Moscow')).time()

    await message.answer(text="Проверка счетов...")

    if current_time >= begin_maintenance or current_time <= end_maintenance:
        await message.answer(text="Технические работы у МосОблЕИРЦ, Мосэнергосбыт")
        try:
            await check_mosru()
        except Exception as exc:
            logger.error(exc)
        try:
            await check_mgts()
        except Exception as exc:
            logger.error(exc)

# 3 because mosru return 2 values
        if zero_cost_count == (3 - check_logs_count):
            await message.answer(text="Неоплаченных счетов не найдено")
        else:
            for text, keyboard in payment_bills_dict.items():
                await message.answer(text=text, reply_markup=keyboard, parse_mode="html")
    else:
        try:
            await check_mosobleirc()
        except Exception as exc:
            logger.error(exc)
        try:
            await check_mosru()
        except Exception as exc:
            logger.error(exc)
        try:
            await check_mgts()
        except Exception as exc:
            logger.error(exc)

# 4 because mosru return 2 values
        if zero_cost_count == (4 - check_logs_count):
            await message.answer(text="Неоплаченных счетов не найдено")
        else:
            for text, keyboard in payment_bills_dict.items():
                await message.answer(text=text, reply_markup=keyboard, parse_mode="html")

    if check_logs_count != 0:
        await message.answer(text="Проверьте логи.")

    zero_cost_count = 0
    check_logs_count = 0
    payment_bills_dict.clear()


class FSMStates(StatesGroup):
    cold_water = State()
    hot_water = State()

    t1 = State()
    t2 = State()
    t3 = State()


def is_integer(n):
    try:
        int(n)
    except ValueError:
        return False
    else:
        return int(n)


@dp.message_handler(text=["Вода"], user_id=11279097)
async def meter_readings_water(message: types.Message):
    await message.answer("Введите показания счетчика холодной воды:", reply_markup=sub_menu)
    await FSMStates.cold_water.set()


@dp.message_handler(state=FSMStates.cold_water, user_id=11279097)
async def cold_water_value(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == "Меню":
        await message.answer(text="Меню", reply_markup=main_menu)
        await state.finish()
    elif answer == "Передать показания":
        await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)
        await state.finish()
    elif is_integer(answer):
        async with state.proxy() as data:
            data["cold_water"] = answer

        await message.answer("Введите показания счетчика горячей воды:")
        await FSMStates.hot_water.set()
    else:
        await message.answer("Введено некорректное значение")


@dp.message_handler(state=FSMStates.hot_water, user_id=11279097)
async def hot_water_value(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == "Меню":
        await message.answer(text="Меню", reply_markup=main_menu)
        await state.finish()
    elif message.text == "Передать показания":
        await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)
        await state.finish()
    elif is_integer(answer):
        data = await state.get_data()
        cold_water = data.get("cold_water")
        hot_water = answer

        await message.answer(f"Холодная вода: {cold_water}")
        await message.answer(f"Горячая вода: {hot_water}")

        await state.finish()
        await message.answer(text="Показания приняты!", reply_markup=sub_menu)
        mosru_water_meter.run(logger, cold_water, hot_water)
    else:
        await message.answer("Введено некорректное значение")


@dp.message_handler(text=["Электричество"], user_id=11279097)
async def meter_readings_electricity(message: types.Message):
    await message.answer("Введите показания пик (T1):", reply_markup=sub_menu)
    await FSMStates.t1.set()


@dp.message_handler(state=FSMStates.t1, user_id=11279097)
async def t1_value(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == "Меню":
        await message.answer(text="Меню", reply_markup=main_menu)
        await state.finish()
    elif answer == "Передать показания":
        await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)
        await state.finish()
    elif is_integer(answer):
        async with state.proxy() as data:
            data["t1"] = answer

        await message.answer("Введите показания ночь (T2):")
        await FSMStates.t2.set()
    else:
        await message.answer("Введено некорректное значение")


@dp.message_handler(state=FSMStates.t2, user_id=11279097)
async def t2_value(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == "Меню":
        await message.answer(text="Меню", reply_markup=main_menu)
        await state.finish()
    elif answer == "Передать показания":
        await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)
        await state.finish()
    elif is_integer(answer):
        async with state.proxy() as data:
            data["t2"] = answer

        await message.answer("Введите показания полупик (T3):")
        await FSMStates.t3.set()
    else:
        await message.answer("Введено некорректное значение")


@dp.message_handler(state=FSMStates.t3, user_id=11279097)
async def t3_value(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == "Меню":
        await message.answer(text="Меню", reply_markup=main_menu)
        await state.finish()
    elif message.text == "Передать показания":
        await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)
        await state.finish()
    elif is_integer(answer):
        data = await state.get_data()
        t1 = data.get("t1")
        t2 = data.get("t2")
        t3 = answer

        await message.answer(f"пик (T1): {t1}")
        await message.answer(f"ночь (T2): {t2}")
        await message.answer(f"полупик (T3): {t3}")

        await state.finish()
        await message.answer(text="Показания приняты!", reply_markup=sub_menu)
        mosru_electricity_meter.run(logger, t1, t2, t3)
    else:
        await message.answer("Введено некорректное значение")


@dp.message_handler(text=["Передать показания"], user_id=11279097)
async def submit_meter_readings(message: types.Message):
    await message.answer(text="Какие показания хотите передать?", reply_markup=meter_readings)


@dp.message_handler(text=["Меню"], user_id=11279097)
async def show_menu(message: types.Message):
    await message.answer(text="Меню", reply_markup=main_menu)


@dp.message_handler(commands=["start"], user_id=11279097)
async def send_welcome(message: types.Message):
    await message.answer(text="Привет!")
    await message.answer(text="Меню", reply_markup=main_menu)


async def schedule_meter_readings(dp):
    await dp.bot.send_message(chat_id=11279097, text="Время передавать показания!", reply_markup=sub_menu)


async def schedule_check_bills(dp):
    global zero_cost_count, check_logs_count

    try:
        await check_mosobleirc()
    except Exception as exc:
        logger.error(exc)
    try:
        await check_mosru()
    except Exception as exc:
        logger.error(exc)
    try:
        await check_mgts()
    except Exception as exc:
        logger.error(exc)

    if len(payment_bills_dict) != 0:
        await dp.bot.send_message(chat_id=11279097, text="Найдены новые счета:")
        for text, keyboard in payment_bills_dict.items():
            await dp.bot.send_message(chat_id=11279097, text=text, reply_markup=keyboard, parse_mode="html")

    if check_logs_count != 0:
        await dp.bot.send_message.answer(chat_id=11279097, text="Проверьте логи.")

    zero_cost_count = 0
    check_logs_count = 0
    payment_bills_dict.clear()


# schedule
scheduler = AsyncIOScheduler()
scheduler.start()


async def schedule_jobs():
    # scheduler.add_job(schedule_check_bills, "interval", minutes=1, args=(dp,))
    scheduler.add_job(schedule_check_bills, "cron", timezone="Europe/Moscow", day="5-19", hour=10, args=(dp,))
    scheduler.add_job(schedule_meter_readings, "cron", timezone="Europe/Moscow", day="18", hour=21, args=(dp,))


async def on_startup(dp):
    await schedule_jobs()

if __name__ == "__main__":
    logger.info("Bot initialized")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    logger.info("Bot stopped")
