import aiosqlite
import aiogram
import random
import os
import aiofiles
import config_data.config

from main import PRIMARY_KEYS


async def connect(typeActions=None, user_id=None, shop_id=None, downloaded_file=None, cod_product=None, data_product=None):
    conn = await aiosqlite.connect('overduo.db')
    if typeActions == 'check_in':
        cursor = await conn.execute('SELECT user_id FROM users')
        users: list[int] = await cursor.fetchall()
        return users
    
    if typeActions == 'add_user':
        await conn.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))

    if typeActions == 'create_shop':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (user_id,))
        await cursor.execute('UPDATE users SET shop_id = ?', (str(shop_id),))
        shops_table = await conn.execute('SELECT shop_id FROM shops')
        await shops_table.execute('INSERT INTO shops (shop_id) VALUES (?)', (shop_id,))
        shops_id_in_folder = ('shops')
        folders = [f for f in os.listdir(shops_id_in_folder) if os.path.isdir(os.path.join(shops_id_in_folder, f))]
        if str(shop_id) not in folders:
            os.makedirs(f'shops/{shop_id}')
            global PRIMARY_KEYS
            PRIMARY_KEYS.add(shop_id)

        await conn.commit()

    if typeActions == 'show_products':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (user_id,))
        cursor = await cursor.fetchone()
        info_product = await conn.execute('SELECT * FROM products WHERE shop_id = ?', (str(cursor[0]), ))
        info_product = await info_product.fetchall()
        return info_product

    if typeActions == 'show':
        # cursor = await conn.execute('SELECT shop_id FROM shops')
        # shops = await cursor.fetchall()
        # shops: list[str] = [str(i[0]) for i in shops]
        # return shops
        return PRIMARY_KEYS
    
    if typeActions == 'add_product':
        cursor = await conn.execute('SELECT shop_id FROM users WHERE user_id = (?)', (user_id,))
        # Выбирает id магазина, к которому подключен пользователь
        cursor = await cursor.fetchone()
        async with aiofiles.open(f'shops/{str(cursor[0])}/{cod_product}.jpg', 'wb') as file:
            await file.write(downloaded_file.getvalue())
        connct_products = await conn.execute('INSERT INTO products (shop_id, cod, data) VALUES (?, ?, ?)', (cursor[0], cod_product, data_product))

    if typeActions == 'clear':
        PRIMARY_KEYS = set()
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
