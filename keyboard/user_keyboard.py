from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

enter_btn = InlineKeyboardButton(text='Войти', callback_data='enterCD')                    # Кнопка Войти
create_btn = InlineKeyboardButton(text='Создать БД магазина', callback_data='createCD')           # Кнопка создать
cancel_btn = InlineKeyboardButton(text='Отмена', callback_data='cancelCD')                 # Кнопка отмены
add_product_btn = InlineKeyboardButton(text='Добавить товар', callback_data='add_prdCD')   # Кнопка добавления товара
del_product_btn = InlineKeyboardButton(text='Удалить товар', callback_data='del_prdCD')    # Кнопка удаления товара
exit_DB_btn = InlineKeyboardButton(text='Выйти из БД', callback_data='exitCD')               # Кнопка выхода из БД
show_products_btn = InlineKeyboardButton(text='Посмотреть список товаров', callback_data='show_prdCD')
over_3_days_btn = InlineKeyboardButton(text='Истекут в ближайшие 3 дня', callback_data='button_3_daysCD') # Кнопка выводящая товару, где срок проходиит в течение 3 дней
del_improper_products_btn = InlineKeyboardButton(text='Удалить несоответствующие формату товары', callback_data='del_improper_productsCD') # Кнопка удаляющая товары с несоответствующей датой
calculation_btn = InlineKeyboardButton(text='Расчитать срок годности', callback_data='calculationCD') # Кнопка расчета срока годности
forward_btn = InlineKeyboardButton(text='>>', callback_data='forwardCD')
backward_btn = InlineKeyboardButton(text='<<', callback_data='backwardCD')
enter_main_menu_btn = InlineKeyboardButton(text='Main menu', callback_data='main_menuCD')
cancel_input_btn = InlineKeyboardButton(text='Cancel', callback_data='cancel_inputCD')

cancel_enter_keyboard = InlineKeyboardBuilder().row(cancel_input_btn, width=1).as_markup()
enter_or_create_keyboard = InlineKeyboardMarkup(inline_keyboard=([enter_btn], [create_btn])) # Клавиатура Входа/создания БД
in_db_keyboard = InlineKeyboardMarkup(inline_keyboard=([add_product_btn], [del_product_btn], [show_products_btn], [over_3_days_btn], [exit_DB_btn], [del_improper_products_btn], [calculation_btn])) # Клавиатура кнопок взаимодействия с БД
enter_create_or_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=([enter_btn], [create_btn], [cancel_btn])) # Клавиатура создания/входа или выхода из БД
pagination_keyboard = InlineKeyboardBuilder().row(backward_btn, forward_btn, enter_main_menu_btn, width=2).as_markup()