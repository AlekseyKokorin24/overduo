from aiogram import Router, types, F, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis

from other_func import connect, create_pimary_keys, calculate_func
from FSM_state import FSM_FORM

from aiogram.types import InlineKeyboardMarkup, CallbackQuery, PhotoSize, FSInputFile

import logging, datetime
from keyboard import *
from main import bot, PRIMARY_KEYS

router = Router()
user_db = {}

logger = logging.getLogger(__name__) 

logger.setLevel(10)
handler = logging.FileHandler('my_log.log', 'a', encoding='utf-8')
formatter = logging.Formatter('[{asctime}] #{levelname} {filename}:{lineno} - {message}', style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Команда для админа, которая очищает состояние машины
@router.message(Command('clear_state'))
async def clear_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('FSM is clear')

# Запуск бота в дефолтном состоянии
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_bot(message: Message):
    await message.answer(text=f'✨<b>{message.from_user.first_name}</b>✨, привет.\n\nЗдесь ты можешь хранить информацию о товарах:<b>\n-Срок годности\n-Фото\n-Код-фрагмент\n-Название товара\n</b>\nНо для начала нужно <b>войти</b> или <b>создать базу магазина</b>', reply_markup=enter_or_create_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    logger.info(f'Пользователь {message.from_user.first_name, message.from_user.last_name} запустил бота')

# Запуск бота НЕ в дефолтном состоянии
@router.message(CommandStart(), ~StateFilter(default_state))
async def process_start_bot(message: Message):
    await message.answer(text='<b>Выбирай</b>', reply_markup=in_db_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

# Отмена входа
@router.callback_query(F.data == 'cancelCD')
async def process_cancel(calback: CallbackQuery, state: FSMContext):
    await calback.message.edit_text('Пробуй еще раз', reply_markup=enter_or_create_keyboard)
    await state.clear()

# Создание магазина в БД
@router.callback_query(F.data == 'createCD')
async def process_enter_shop_id(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[enter_btn]])
    key = create_pimary_keys()
    await connect(typeActions='create_shop_TA', shop_id=key, user_id=callback.message.from_user.id)
    await callback.message.edit_text(f'Вот твой уникальный <b>id</b> магазина - <b>{key}</b>\nЗапонимни его, потому что сейчас он удалися', reply_markup=keyboard)
    logger.info(f'Был создан магазин: {key}')

# Вход в БД в дефолтном состоянии
@router.callback_query(F.data == 'enterCD', StateFilter(default_state))
async def process_enter_shop(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await callback.message.edit_text('Введи <b>id</b> магазина для входа', reply_markup=keyboard)
    await state.set_state(FSM_FORM.stateWaitingShopId)
    
# Ожидание ввода кода магазина
@router.message(StateFilter(FSM_FORM.stateWaitingShopId), F.text.in_(PRIMARY_KEYS))  # Delete StateFilter(FSM_FORM.stateBeingInDB)
async def process_set_shop_id(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await connect(typeActions='enter_shop_TA', shop_id=message.text, user_id=message.from_user.id)
    await message.answer('Поздравляю, ты вошел👏', reply_markup=in_db_keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

# Ошибка входа
@router.message(StateFilter(FSM_FORM.stateWaitingShopId))
async def warning(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_btn]])
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Лолик блин\n\nПопробуй еще раз\nИли создай новый', reply_markup=keyboard)

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
    await calback.message.edit_text('Пожалуйста, отправь фото товара.\n\nВ описании к нему отправь:\n1. Код-фрагмент\n2. Дату, до которого товар годен\n  <b>В формате ДД.ММ.ГГГГ</b>\n3. название товара(опицонально)', reply_markup=cancel_enter_keyboard)
    await state.set_state(FSM_FORM.stateWaitingInfoProducts)

# Проверяет, что отправлено фото, дата соответствует формату и добавялет товар в БД
@router.message(StateFilter(FSM_FORM.stateWaitingInfoProducts), F.photo[-1].as_('largest_photo'))
async def process_set_photo_product(message: Message, state: FSMContext, largest_photo: PhotoSize):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    photo_id = message.photo[-1].file_id
    file_info = await bot.get_file(photo_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    try:
        caption = message.caption.split()
        cod_product = caption[0]
        date_poduct = caption[1]
        name_product = caption[2]
        assert cod_product.isdigit()
        datetime.datetime.strptime(date_poduct, "%d.%m.%Y")
        await connect(typeActions='add_product_TA', downloaded_file=downloaded_file, cod_product=cod_product, data_product=date_poduct, user_id=message.from_user.id, name_product=name_product)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await state.update_data(
            photo_unique_id=largest_photo.file_unique_id,
            photo_id=largest_photo.file_id
            )
        # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.answer('<b>Красава</b>, товар добавлен в БД твоего магазина', reply_markup=in_db_keyboard)
        await state.set_state(FSM_FORM.stateBeingInDB)
    except Exception as ex:
        logger.error(f'Произошла ошибка: {ex}')
        # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await state.set_state(FSM_FORM.stateBeingInDB)
        await message.answer('Произошла оишбка\nПроверь правильность введенных данных.', reply_markup=in_db_keyboard)

@router.message(StateFilter(FSM_FORM.stateWaitingInfoProducts))
async def wrang_set_photo_products(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await state.set_state(FSM_FORM.stateBeingInDB)
    await message.answer(f'<b>Произошла оибка</b>\n\nПроверь, что отправляешь фото', reply_markup=in_db_keyboard)

# Показывает все продукты, которые нахоядятся в БД
@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'show_prdCD')
async def show_products(callback: CallbackQuery):
    user_db[callback.from_user.id] = await connect(typeActions='show_products_TA', user_id=callback.from_user.id)
    if not user_db[callback.from_user.id]:
        await callback.message.edit_text('<b>Нет товаров</b>', reply_markup=in_db_keyboard)
    else:
        page = user_db[callback.from_user.id]['page']
        if page == 1:
            await callback.message.edit_text(user_db[callback.from_user.id][1], reply_markup=cancel_enter_keyboard)
        else:
            await callback.message.edit_text(user_db[callback.from_user.id][page], reply_markup=pagination_keyboard)

# @router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'backwardCD')
# async def process_backward_pegination(callback: CallbackQuery):
#     page = user_db[callback.from_user.id]['page'] 
#     try:
#         await callback.message.edit_text(user_db[callback.from_user.id][page-1], reply_markup=pagination_keyboard)
#         user_db[callback.from_user.id]['page'] -= 1
#     except:
#         page = user_db[callback.from_user.id]['lenth']
#         await callback.message.edit_text(user_db[callback.from_user.id][page], reply_markup=pagination_keyboard)
#         user_db[callback.from_user.id]['page'] = page

# @router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'forwardCD')
# async def process_backward_pegination(callback: CallbackQuery):
#     page = user_db[callback.from_user.id]['page'] 
#     # await callback.message.edit_text(f'Это всё\n{user_db[callback.from_user.id][1]}', cancel_input_btn)
#     await callback.message.edit_text(user_db[callback.from_user.id][1], reply_markup=cancel_input_btn)
#     try:
#         if page < 10:
#             page += 1
#             await callback.message.edit_text(user_db[callback.from_user.id][page], reply_markup=pagination_keyboard)
#             user_db[callback.from_user.id]['page'] += 1
#         else:
#             await callback.message.answer('lol')
#     except: send_message
#         user_db[callback.from_user.id]['page'] = 1
#         await callback.message.edit_text(user_db[callback.from_user.id][1], reply_markup=pagination_keyboard)

@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data.in_(['backwardCD', 'forwardCD']))
async def process_pagination(callback: CallbackQuery):
    page = user_db[callback.from_user.id]['page']
    try:
        if callback.data == 'backwardCD':
            await callback.message.edit_text(user_db[callback.from_user.id][page-1], reply_markup=pagination_keyboard)
            user_db[callback.from_user.id]['page'] -=1
        elif callback.data == 'forwardCD':
            await callback.message.edit_text(user_db[callback.from_user.id][page+1], reply_markup=pagination_keyboard)
            user_db[callback.from_user.id]['page'] +=1
    except:
        if callback.data == 'backwardCD':
            page = user_db[callback.from_user.id]['lenth']
            await callback.message.edit_text(user_db[callback.from_user.id][page], reply_markup=pagination_keyboard)
            user_db[callback.from_user.id]['page'] = page
        elif callback.data == 'forwardCD':
            await callback.message.edit_text(user_db[callback.from_user.id][1], reply_markup=pagination_keyboard)
            user_db[callback.from_user.id]['page'] = 1

@router.callback_query(F.data == 'main_menuCD')
async def enter_main_menu_btn(callback: CallbackQuery):
    await callback.message.edit_text('<b>Продолжим</b>', reply_markup=in_db_keyboard)
# Показывает товары, у которых срок годности выходит в течение 3 дней
@router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data.in_(['3_daysCD, 15_daysCD']))
async def overduo_3_days(callback: CallbackQuery):
    if callback.data == '3_daysCD':
        fit_date = await connect(typeActions='enter_3_days_TA', user_id=callback.from_user.id)
    elif callback.data == '15_daysCD':
        fit_date = await connect(typeActions='enter_15_days_TA', user_id=callback.from_user.id)
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    if fit_date:
        for i in fit_date:
            photo = FSInputFile(f"shops/{str(i[0])}/{str(i[1])}.jpg")
            await callback.message.answer_photo(photo=photo, caption=f'<b>Название:</b> {i[3]}\nКод товара: <b>{i[1]}</b>, Годен до: <b>{i[2]}</b>')
        await callback.message.answer(text='<b>Продолжим</b>', reply_markup=in_db_keyboard)
    else:
        await callback.message.edit_text(text="<b>Нет подходящих дат</b>", reply_markup=in_db_keyboard)

# @router.callback_query(StateFilter(FSM_FORM.stateBeingInDB), F.data == 'del_improper_productsCD')
# async def del_improper_products(callback: CallbackQuery, state: FSMContext):
#     await connect(typeActions='del_improper_products_TA', user_id=callback.from_user.id)
#     await callback.message.edit_text(text='\n<b>Все лишние файлы удалены</b>\n', reply_markup=in_db_keyboard)
#     await state.set_state(FSM_FORM.stateBeingInDB)

# Функция расчета срока годности
@router.callback_query(F.data == 'calculationCD', StateFilter(FSM_FORM.stateBeingInDB))
async def wait_calculate(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('<b>Введите через пробел</b>:\n\n1. Дату изготовления [ДД.ММ.ГГГГ]\n2. Срок годности\n3. Формат расчета (д/м/г)', reply_markup=cancel_enter_keyboard)
    await state.set_state(FSM_FORM.stateCalculate)

@router.message(StateFilter(FSM_FORM.stateCalculate), F.text.split().len() == 3)
async def calculate(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    date_create, num, form = message.text.split()
    new_date = calculate_func(date_create, int(num), form)
    if new_date:
        await message.answer(f"Товар годен до <b>{str(new_date)}</b>",reply_markup=in_db_keyboard)
        await state.set_state(FSM_FORM.stateBeingInDB)
    else:
        await message.answer('<b>Где-то ошибка</b>\n Проверь правильность введенных данных', reply_markup=in_db_keyboard)
        await state.set_state(FSM_FORM.stateBeingInDB)

@router.message(StateFilter(FSM_FORM.stateCalculate))
async def wrang_data(message: Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer('<b>Введи в правильном формате</b>\n\nВведите через пробел:\n1.Дату изготовления [ДД.ММ.ГГГГ]\n2.Срок годности\n3.Формат расчета (д/м/г)', reply_markup=cancel_enter_keyboard)


@router.callback_query(F.data == 'del_prdCD', StateFilter(FSM_FORM.stateBeingInDB))
async def wait_del_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Отправь код-фрагмент товара без первых нулей', reply_markup=cancel_enter_keyboard)
    await state.set_state(FSM_FORM.stateWaitingDeleteProducts)

@router.message(StateFilter(FSM_FORM.stateWaitingDeleteProducts))
async def del_products(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    result = await connect(typeActions='del_products_TA', cod_product=message.text)
    if result == False:
        await message.answer('<b>Произошла ошибка</b>\nПопробуй ввести другой код', reply_markup=in_db_keyboard)

    else:
        await message.answer('<b>Товар удален</b>', reply_markup=in_db_keyboard)

    await state.set_state(FSM_FORM.stateBeingInDB)
        
@router.callback_query(F.data == 'cancel_inputCD')
async def cancel_enter(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('<b>Продолжим</b>', reply_markup=in_db_keyboard)
    await state.set_state(FSM_FORM.stateBeingInDB)

@router.message(Command('master'))
async def show_master_splinter(message: Message):
    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await message.answer('Великий мастер Сплинтер в этом месяце:\n<b>Вячеслав Павлюк</b>')
    logger.info('Вызвана функция /master')