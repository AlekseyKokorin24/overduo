from aiogram import Router, types, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis

from other_func import connect, create_pimary_keys, calculate_func
from FSM_state import FSM_FORM

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, PhotoSize, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import logging
from keyboard import *
from main import bot, PRIMARY_KEYS

router = Router()

# Запуск бота в дефолтном состоянии
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_bot(message: Message):
    await message.answer(text='Привет, говно', reply_markup=enter_or_create_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

# Запуск бота НЕ в дефолтном состоянии
@router.message(CommandStart(), ~StateFilter(default_state))
async def process_start_bot(message: Message):
    await message.answer(text='Выбирай, говно', reply_markup=in_db_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

# Отмена входа
@router.callback_query(F.data == 'cancelCD')
async def process_cancel(calback: CallbackQuery, state: FSMContext):
    await calback.message.edit_text('Попробуем снова в другой раз', reply_markup=enter_or_create_keyboard)
    await state.clear()

# Создание магазина в БД
@router.callback_query(F.data == 'createCD')
async def process_enter_shop_id(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter_btn]])
    key = create_pimary_keys()
    await connect(typeActions='create_shop_TA', shop_id=key, user_id=callback.message.from_user.id)
    await callback.message.edit_text(f'Вот ваш уникальный id магазина - {key}\nЗапонимните его, потому что сейчас удалися', reply_markup=keyboard)
    
# Вход в БД в дефолтном состоянии
@router.callback_query(F.data == 'enterCD', StateFilter(default_state))
async def process_enter_shop(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await callback.message.edit_text('Пожалуйста, введите id магазина', reply_markup=keyboard)
    await state.set_state(FSM_FORM.stateWaitingShopId)
    
# Ожидание ввода кода магазина
@router.message(StateFilter(FSM_FORM.stateWaitingShopId), F.text.in_(PRIMARY_KEYS))  # Delete StateFilter(FSM_FORM.stateBeingInDB)
async def process_set_shop_id(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await connect(typeActions='enter_shop_TA', shop_id=message.text, user_id=message.from_user.id)
    await message.answer('Поздравляю, вы вошли💦', reply_markup=in_db_keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

# Ошибка входа
@router.message(StateFilter(FSM_FORM.stateWaitingShopId))
async def warning(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Лолик блин\n\nПопробуй еще раз😡\nИли создай новый', reply_markup=keyboard)

# Выход из БД в состоянии нахождения в БД
@router.callback_query(F.data == 'exitCD', ~StateFilter(default_state))
async def process_exit(calback: CallbackQuery, state: FSMContext):
    await connect(typeActions='exit_db_TA', user_id=calback.from_user.id)
    await calback.message.edit_text('Выполнен выход из БД', reply_markup=enter_or_create_keyboard)
    await state.clear()

# Показать список магазинов
@router.message(F.text.startswith('/show'))
async def show(message: Message):
    shops = await connect(typeActions='show_TA')
    await message.answer(str(shops))

# Добавить товар в состоянии нахождения в БД
@router.callback_query(F.data == 'add_prdCD', StateFilter(FSM_FORM.stateBeingInDB))
async def add_product(calback: CallbackQuery, state: FSMContext):
    await calback.message.edit_text('Пожалуйста, отправь фото товара и его код-фрагмент и через пробел до какого числа годен\nВ формате ДД.ММ.ГГГГ')
    await state.set_state(FSM_FORM.stateWaitingInfoProducts)


@router.message(StateFilter(FSM_FORM.stateWaitingInfoProducts), F.photo[-1].as_('largest_photo'))
async def process_set_photo_product(message: Message, state: FSMContext, largest_photo: PhotoSize):
    photo_id = message.photo[-1].file_id
    file_info = await bot.get_file(photo_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    cod_product = message.caption.split()[0]
    data_poduct = message.caption.split()[1]
    await connect(typeActions='add_product_TA', downloaded_file=downloaded_file, cod_product=cod_product, data_product=data_poduct, user_id=message.from_user.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
        )
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer('Красава, товар добавлен', reply_markup=in_db_keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

# Показывает все продукты, которые нахоядятся в БД
@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'show_prdCD')
async def show_products(callback: CallbackQuery):
    info_product = await connect(typeActions='show_products_TA', user_id=callback.from_user.id)
    if info_product:
        for i in info_product:
            photo = FSInputFile(f'shops/{str(i[0])}/{str(i[1])}.jpg')
            await callback.message.answer_photo(photo=photo, caption=f'Код товара: {i[1]}\nСрок годности до: {i[2]}')
    else:
        await callback.message.edit_text(text='Товаров пока нет')
    await callback.message.answer(text='Продолжим', reply_markup=in_db_keyboard)

# Показывает товары, у которых срок годности выходит в течение 3 дней
@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'button_3_daysCD')
async def overduo_3_days(callback: CallbackQuery):
    fit_date = await connect(typeActions='enter_3_days_TA', user_id=callback.from_user.id)
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if fit_date:
        for i in fit_date:
            photo = FSInputFile(f"shops/{str(i[0])}/{str(i[1])}.jpg")
            await callback.message.answer_photo(photo=photo, caption=f'Код товара {i[1]}')
        await callback.message.answer(text='Продолжим', reply_markup=in_db_keyboard)
    else:
        await callback.message.answer(text="Нет подходящих дат", reply_markup=in_db_keyboard)

@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'del_improper_productsCD')
async def del_improper_products(callback: CallbackQuery):
    await connect(typeActions='del_improper_products_TA', user_id=callback.from_user.id)
    await callback.message.edit_text(text='Все лишние файлы удалены', reply_markup=in_db_keyboard)


@router.callback_query(F.data == 'calculationCD', StateFilter(FSM_FORM.stateBeingInDB))
async def wait_calculate(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите через прбел дату изготовления, срок годности и формат расчета (д/м/г)')
    await state.set_state(FSM_FORM.stateCalculate)

@router.message(StateFilter(FSM_FORM.stateCalculate))
async def calculate(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    date_create, num, form = message.text.split()
    new_date = calculate_func(date_create, int(num), form)
    await message.answer(f"Товар годен до {str(new_date)}",reply_markup=in_db_keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

