from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

enter = InlineKeyboardButton(text='ВОЙТИ💨', callback_data='enter')                    # Кнопка Войти
create = InlineKeyboardButton(text='СОЗДАТЬ БАЗУ💥', callback_data='create')           # Кнопка создать
cancel = InlineKeyboardButton(text='ОТМЕНА💤', callback_data='cancel')                 # Кнопка отмены
add_product_btn = InlineKeyboardButton(text='ДОБАВИТЬ ТОВАР🍗', callback_data='add_prd')   # Кнопка добавления товара
del_product_btn = InlineKeyboardButton(text='УДАЛИТЬ ТОВАР❌', callback_data='del_prd')    # Кнопка удаления товара
exit_DB = InlineKeyboardButton(text='ВЫЙТИ ИЗ БД', callback_data='exit')               # Кнопка выхода из БД
show_products_btn = InlineKeyboardButton(text='ПОСМОТРЕТЬ СПИСОК ТОВАРОВ', callback_data='show_prd')