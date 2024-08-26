import aiosqlite
import aiogram
import random
import os
import aiofiles
import datetime as dt

from main import PRIMARY_KEYS

def select_3_days(date: str):
    if len(date) < 10:
        return 100
    d1 = dt.datetime.strptime(date, "%d.%m.%Y")
    d2 = dt.datetime.strptime(str(dt.date.today()), "%Y-%m-%d")
    return (d1 - d2).days

async def connect(typeActions=None, user_id=None, shop_id=None, downloaded_file=None, cod_product=None, data_product=None):
    conn = await aiosqlite.connect('overduo.db')

    if typeActions == 'create_shop_TA':
        await conn.execute('INSERT INTO users (shop_id) VALUES (?)', (shop_id, ))
        os.makedirs(f'shops/{shop_id}')
        global PRIMARY_KEYS 
        PRIMARY_KEYS.add(shop_id)

    if typeActions == 'enter_shop_TA':
        await conn.execute('UPDATE users SET user_id = ? WHERE shop_id = ?', (user_id, shop_id))
        await conn.commit()
        crsr = await conn.execute("SELECT shop_id FROM users WHERE user_id = ?", (user_id, ))
        crsr = await crsr.fetchone()

    if typeActions == 'exit_db_TA':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (int(user_id), ))
        cursor = await cursor.fetchone()
        await conn.execute('UPDATE users SET user_id = NULL WHERE shop_id = ?', (cursor[0], ))

    if typeActions == 'show_products_TA':
        cursor = await conn.execute("SELECT shop_id FROM users WHERE user_id = (?)", (user_id, ))
        cursor = await cursor.fetchone()
        info_product = await conn.execute("SELECT * FROM products WHERE shop_id = (?)", (str(cursor[0]), ))
        info_product = await info_product.fetchall()
        return info_product

    if typeActions == 'show_TA':
        return PRIMARY_KEYS
    
    if typeActions == 'add_product_TA':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (user_id,))
        cursor = await cursor.fetchone()
        async with aiofiles.open(f'shops/{str(cursor[0])}/{cod_product}.jpg', 'wb') as file:
            await file.write(downloaded_file.getvalue())
        await conn.execute('INSERT INTO products (shop_id, cod, data) VALUES (?, ?, ?)', (cursor[0], cod_product, data_product))

    if typeActions == 'clear_TA':
        PRIMARY_KEYS = set()

    if typeActions == 'enter_3_days_TA':
        cursor = await conn.execute("SELECT shop_id FROM users WHERE user_id = (?)", (user_id, ))
        cursor = await cursor.fetchone()
        fit_products = await conn.execute('SELECT * FROM products WHERE shop_id = (?)', (cursor[0], ))
        fit_products = await fit_products.fetchall()
        return [i for i in fit_products if select_3_days(i[2]) <= 3]
    await conn.commit()
    await conn.close() 

def create_pimary_keys():
    while True:
        key = ''
        for _ in range(3):
            key += str(random.randint(1, 9))
        key += '-'
        for _ in range(3):
            key += str(random.randint(1, 9))
        return key
