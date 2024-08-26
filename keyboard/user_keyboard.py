from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

enter_btn = InlineKeyboardButton(text='ВОЙТИ💨', callback_data='enterCD')                    # Кнопка Войти
create_btn = InlineKeyboardButton(text='СОЗДАТЬ БАЗУ💥', callback_data='createCD')           # Кнопка создать
cancel_btn = InlineKeyboardButton(text='ОТМЕНА💤', callback_data='cancelCD')                 # Кнопка отмены
add_product_btn = InlineKeyboardButton(text='ДОБАВИТЬ ТОВАР🍗', callback_data='add_prdCD')   # Кнопка добавления товара
del_product_btn = InlineKeyboardButton(text='УДАЛИТЬ ТОВАР❌', callback_data='del_prdCD')    # Кнопка удаления товара
exit_DB_btn = InlineKeyboardButton(text='ВЫЙТИ ИЗ БД', callback_data='exitCD')               # Кнопка выхода из БД
show_products_btn = InlineKeyboardButton(text='ПОСМОТРЕТЬ СПИСОК ТОВАРОВ', callback_data='show_prdCD')
over_3_days_btn = InlineKeyboardButton(text='Продукты, исходящие в течение 3 дней', callback_data='button_3_daysCD') # Кнопка выводящая товару, где срок проходиит в течение 3 дней

enter_or_create_keyboard = InlineKeyboardMarkup(inline_keyboard=([enter_btn], [create_btn])) # Клавиатура Входа/создания БД
in_db_keyboard = InlineKeyboardMarkup(inline_keyboard=([add_product_btn], [del_product_btn], [show_products_btn], [over_3_days_btn], [exit_DB_btn])) # Клавиатура кнопок взаимодействия с БД
enter_create_or_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=([enter_btn], [create_btn], [cancel_btn])) # Клавиатура создания/входа или выхода из БД
