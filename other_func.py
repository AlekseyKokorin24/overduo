# Работа с асинхронными модулями
import aiofiles.os, aiosqlite, aiofiles
# Работа с файлами 
import os
# Работа с датами 
import datetime as dt
from dateutil.relativedelta import relativedelta
# Другие модули
import random, re
# Переменные из других файлов 
from main import PRIMARY_KEYS
from main import bot

# Выбор элементов с неправильным форматом даты
def select_improper_date(date):
    pattern = re.compile(r'\d\d\.\d\d\.\d\d\d\d')
    if pattern.search(date) is None:
        return True

# Функция расчета срока годности
def calculate_func(date_create: str, num: int, form: str):
    try:
        d1 = dt.datetime.strptime(date_create, '%d.%m.%Y')
        if form == 'м':
            new_date = d1 + relativedelta(months=num)
        if form == 'д':
            new_date = d1 + dt.timedelta(days=num)
        return dt.datetime.strftime(new_date, '%d-%m-%Y')
    except:
        return False
# Функция выбора товаров, с исходящим сроком годнсти в течение 3 дней
def select_3_days(date: str):
    if len(date) < 10:
        return 100
    d1 = dt.datetime.strptime(date, "%d.%m.%Y")
    d2 = dt.datetime.strptime(str(dt.date.today()), "%Y-%m-%d")
    return (d1 - d2).days

# Функция создания ключа к БД    
def create_pimary_keys():
    while True:
        key = ''
        for _ in range(3):
            key += str(random.randint(1, 9))
        key += '-'
        for _ in range(3):
            key += str(random.randint(1, 9))
        return key
    
# Основная функция работы с БД
async def connect(typeActions=None, user_id=None, shop_id=None, downloaded_file=None, cod_product=None, data_product=None, name_product=None):
    conn = await aiosqlite.connect('overduo.db') # Подключение в БД

    # При создании магазина добавляется shop_id магазина в таблицу users
    if typeActions == 'create_shop_TA':
        await conn.execute('INSERT INTO users (shop_id) VALUES (?)', (shop_id, ))
        os.makedirs(f'shops/{shop_id}')
        global PRIMARY_KEYS 
        PRIMARY_KEYS.add(shop_id)

    # Вход в БД магазина 
    if typeActions == 'enter_shop_TA':
        await conn.execute('UPDATE users SET user_id = ? WHERE shop_id = ?', (user_id, shop_id))
        await conn.commit()
        crsr = await conn.execute("SELECT shop_id FROM users WHERE user_id = ?", (user_id, ))
        crsr = await crsr.fetchone()

    # Выход из БД магазина
    if typeActions == 'exit_db_TA':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (int(user_id), ))
        cursor = await cursor.fetchone()
        await conn.execute('UPDATE users SET user_id = NULL WHERE shop_id = ?', (cursor[0], ))

    # Посмотреть все продукты, добавленные в базу данных 
    if typeActions == 'show_products_TA':
        cursor = await conn.execute("SELECT shop_id FROM users WHERE user_id = (?)", (user_id, ))
        cursor = await cursor.fetchone()
        info_products = await conn.execute("SELECT * FROM products WHERE shop_id = (?)", (str(cursor[0]), ))
        info_products = await info_products.fetchall()
        if not info_products:
            return False
        result = []
        res = []
        count = 1
        for product in info_products:
            string = f'{product[3]}, Код: {str(product[1])}, Годен до: {product[2]}'
            res.append(string)
            count += 1
            if count % 7 == 0:
                result.append('\n'.join(res))
                res = []
                count += 1
        
        result.append('\n'.join(res)) if res else None
        user_dict = {key: value for key, value in enumerate(result, start=1)}
        lenth = len(user_dict)
        user_dict['page'] = 1
        user_dict['lenth'] = lenth
        return user_dict
    
    # Для администратора бота, показывает все магазины
    if typeActions == 'show_TA':
        return PRIMARY_KEYS
    
    # Добавить товар в БД магазина 
    if typeActions == 'add_product_TA':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (user_id,))
        cursor = await cursor.fetchone()
        print(cursor[0])
        async with aiofiles.open(f'shops/{cursor[0]}/{cod_product}.jpg', 'wb') as file:
            await file.write(downloaded_file.getvalue())
        await conn.execute('INSERT INTO products (shop_id, cod, data, name_product) VALUES (?, ?, ?, ?)', (cursor[0], cod_product, data_product, name_product))

    # Для алминистратора бота, очищает список магазинов 
    if typeActions == 'clear_TA':
        PRIMARY_KEYS = set()

    # Выбор товаров, срок годности которых уходит в течение 3 дней
    if typeActions == 'enter_3_days_TA':
        cursor = await conn.execute("SELECT shop_id FROM users WHERE user_id = (?)", (user_id, ))
        cursor = await cursor.fetchone()
        fit_products = await conn.execute('SELECT * FROM products WHERE shop_id = (?)', (cursor[0], ))
        fit_products = await fit_products.fetchall()
        return [i for i in fit_products if select_3_days(i[2]) <= 3]
    
    # Удаление товаров, с неподходящей датой 
    if typeActions == 'del_improper_products_TA': 
        cursor = await conn.execute("SELECT shop_id FROM users WHERE user_id = (?)", (user_id, ))
        cursor = await cursor.fetchone()
        cursor = await conn.execute('SELECT * FROM products WHERE shop_id = (?)', (cursor[0], ))
        cursor = await cursor.fetchall()
        for i in cursor:
            if select_improper_date(i[2]):
                await conn.execute('DELETE FROM products WHERE data = (?)', (i[2], ))
                file_name = f'shops/{str(i[0])}/{str(i[1])}.jpg'
                os.remove(file_name)
    
    if typeActions == 'del_products_TA':
        cursor = await conn.execute("SELECT * FROM products WHERE cod = (?)", (cod_product, ))
        cursor = await cursor.fetchone()
        try:
            await conn.execute("DELETE FROM products WHERE cod = (?)", (cod_product, ))
            file_name = f'shops/{str(cursor[0])}/{str(cursor[1])}.jpg'
            os.remove(file_name)
        except Exception as ex:
            print(ex)
            return False
    await conn.commit()
    await conn.close() 

