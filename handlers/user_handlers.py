from aiogram import Router, types, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from other_func import connect, create_pimary_keys
from main import PRIMARY_KEYS
from FSM_state import FSM_FORM

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, PhotoSize
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import aiosqlite, asyncio, logging, os
from keyboard import *
from main import bot

router = Router()

# Запуск бота в дефолтном состоянии
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_bot(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter], [create]])
    id_users = message.from_user.id
    users = await connect(typeActions='check_in')
    if id_users not in users:
        await connect(typeActions='add_user', user_id=id_users)

    await message.answer(text='Привет, говно', reply_markup=keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

# Запуск бота НЕ в дефолтном состоянии
@router.message(CommandStart(), ~StateFilter(default_state))
async def process_start_bot(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_product_btn], [del_product_btn], [exit_DB]])
    await message.answer(text='Выбирай, говно', reply_markup=keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

# Отмена входа
@router.callback_query(F.data == 'cancel')
async def process_cancel(calback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter], [create]])
    await calback.message.edit_text('Попробуем снова в другой раз', reply_markup=keyboard)
    await state.clear()

# Создание магазина в БД
@router.callback_query(F.data == 'create')
async def process_enter_shop_id(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter]])
    key = create_pimary_keys()
    await connect(typeActions='create_shop', shop_id=str(key), user_id=int(callback.message.from_user.id))
    await callback.message.edit_text(f'Вот ваш уникальный id магазина - {key}\nЗапонимните его, потому что сейчас удалися', reply_markup=keyboard)
    
# Вход в БД в дефолтном состоянии
@router.callback_query(F.data == 'enter', StateFilter(default_state))
async def process_enter_shop(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    await callback.message.edit_text('Пожалуйста, введите id магазина', reply_markup=keyboard)
    await state.set_state(FSM_FORM.stateWaitingShopId)

# Нажатие на копку "ВОЙТИ" в состоянии нахождения в БД, Но пока нет возможности вызова данной функции
@router.callback_query(F.data == 'enter', StateFilter(FSM_FORM.stateBeingInDB))
async def warning_enter(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[exit_DB], [cancel]])
    await callback.message.answer('Вы уже находитесь в БД\nСначала нужно выйти', reply_markup=keyboard)
    
# Ожидание ввода кода магазина
@router.message((StateFilter(FSM_FORM.stateWaitingShopId) or StateFilter(FSM_FORM.stateBeingInDB)), F.text.in_(PRIMARY_KEYS))
async def process_set_shop_id(message: Message, state: FSMContext):
    # await connect(bd='overduo.db', typeActions='create_shop',shop_id=message.text, user_id=message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_product_btn], [del_product_btn], [exit_DB]])
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer('Поздравляю, вы вошли💦', reply_markup=keyboard)
    # await state.set_state(FSM_FORM.state_shop_id)
    await state.set_state(FSM_FORM.stateBeingInDB)

# Ошибка входа
@router.message(StateFilter(FSM_FORM.stateWaitingShopId))
async def warning(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel]])
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Лолик блин\n\nПопробуй еще раз😡\nИли создай новый', reply_markup=keyboard)

# Выход из БД в состоянии нахождения в БД
@router.callback_query(F.data == 'exit', ~StateFilter(default_state))
async def process_exit(calback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter], [create]])
    await calback.message.edit_text('Выполнен выход из БД', reply_markup=keyboard)
    await connect(typeActions='exit_db', user_id=calback.message.from_user.id)
    await state.clear()

# Показать список магазинов
@router.message(F.text.startswith('/show'))
async def show(message: Message):
    shops = await connect(typeActions='show')
    await message.answer(str(shops))

# Добавить товар в состоянии нахождения в БД
@router.callback_query(F.data == 'add_prd', StateFilter(FSM_FORM.stateBeingInDB))
async def add_product(calback: CallbackQuery, state: FSMContext):
    # await bot.delete_message(chat_id=calback.message.chat.id, message_id=calback.message.message_id - 1)
    await calback.message.edit_text('Пожалуйста, отправь фото товара и его код-фрагмент и через пробел до какого числа годен')
    await state.set_state(FSM_FORM.stateWaitingInfoProducts)


@router.message(StateFilter(FSM_FORM.stateWaitingInfoProducts), F.photo[-1].as_('largest_photo'))
async def process_set_photo_product(message: Message, state: FSMContext, largest_photo: PhotoSize):
    photo_id = message.photo[-1].file_id
    file_info = await bot.get_file(photo_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    cod_product = message.caption.split()[0]
    data_poduct = message.caption.split()[1]
    await connect(typeActions='add_product', downloaded_file=downloaded_file, cod_product=cod_product, data_product=data_poduct, user_id=message.from_user.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
        )
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add_product_btn], [del_product_btn], [show_products_btn], [exit_DB]])
    await message.answer('Красава, товар добавлен', reply_markup=keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

# В разработке
@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'show_prd')
async def show_products(callback: CallbackQuery):
    info_product = await connect(typeActions='show_products', user_id=int(callback.message.from_user.id))
    for i in info_product:
        await callback.message.answer(f'{str(i[0])}, {str(i[1])}, {str(i[2])}')

# @router.message(Command(commands='clear_key'))
# async def clear_key(message: Message):
#     await connect(typeActions='clear')
#     await message.answer('База очищена')