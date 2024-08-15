import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F, html
from aiogram import types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from api_requests import check_exists, add_user

load_dotenv()

TOKEN = os.getenv("TOKEN")
dp = Dispatcher(storage=MemoryStorage())


class Registration(StatesGroup):
    name = State()
    grade = State()
    phone_number = State()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user = await check_exists(message.from_user.id)
    if len(user) != 0:
        await message.answer(
            "Siz ro'yxatdan o'tkansiz✅\nSizni 25.08.2024 sanada kutib qolamiz.\nBarcha yangiliklarni ushbu telegram kanalda e'lon qilamiz @nurlikelajakkarakul")
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"📝 Ro'yxatdan o'tish", callback_data=f"registration_{message.from_user.id}")
        await message.answer(
            f"Assalomu aleykum {html.bold(message.from_user.full_name)}!\nNurli Kelajak Qorako'l maktabi tashkillashtirayotgan matematika olimpiadasiga ro'yxatdan o'tish uchun ro'yxatdan o'tish tugmasini bosing.",
            reply_markup=builder.as_markup()
        )


@dp.callback_query(lambda c: c.data.startswith("registration"))
async def handler_registration(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.data.split("_")[-1]
    user = await check_exists(user_id)
    print(user)
    if len(user) != 0:
        await callback_query.message.edit_text(
            "Siz ro'yxatdan o'tkansiz✅\nSizni 25.08.2024 sanada kutib qolamiz.\nBarcha yangiliklarni ushbu telegram kanalda e'lon qilamiz @nurlikelajakkarakul")
    else:
        await callback_query.message.edit_text("Ro'yxatdan o'tish boshlandi")
        await callback_query.message.answer(f"{html.bold("Ism familiyangizni")} yozib yuboring: ")
        await state.set_state(Registration.name)


@dp.message(Registration.name)
async def handler_name(message: types.Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)

    builder = InlineKeyboardBuilder()
    for i in range(5, 8):
        builder.button(text=f"{i}", callback_data=f"{i}-sinf")

    for i in range(8, 11):
        builder.button(text=f"{i}", callback_data=f"{i}-sinf")
    builder.adjust(3, 3)

    await message.answer(f"{html.bold("Sinfingizni")} tanlang: ", reply_markup=builder.as_markup())
    await state.set_state(Registration.grade)


@dp.callback_query(Registration.grade)
async def handler_grade(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(f"{callback.data} tanladingiz")
    await state.update_data(grade=callback.data)
    await callback.message.answer(f"{html.bold("Telefon raqamingizni")} yozing: ")
    await state.set_state(Registration.phone_number)


@dp.message(F.content_type == ContentType.TEXT, Registration.phone_number)
async def handler_phone(message: types.Message, state: FSMContext) -> None:
    if message.text and (message.text.isnumeric() or (message.text[0] == "+" and message.text[1:].isnumeric())) and len(
            message.text) >= 9:
        await state.update_data(phone_number=message.text)
        data = await state.get_data()
        name = data["name"]
        grade = data["grade"]
        phone_number = data["phone_number"]
        telegram_id = message.from_user.id

        response = await add_user(name, grade, phone_number, telegram_id)
        if response.get('id'):
            await message.answer(
                "Ro'yxatdan o'tdingiz ✅\nSizni 25.08.2024 sanada kutib qolamiz.\nBarcha yangiliklarni ushbu telegram kanalda e'lon qilamiz @nurlikelajakkarakul")
            await state.clear()
        else:
            await message.answer("Tizimda nosozlik admin bilan bog'laning @nurlikelajakadmin")
    else:
        await message.answer("Telefon raqamni to'g'ri kiriting\nnamuna: +998xxxxxxxxx")
        return


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
