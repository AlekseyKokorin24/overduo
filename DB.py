import aiosqlite
import asyncio



async def main():
    async with (aiosqlite.connect('overduo.db')) as conn:
        await conn.execute('''
                        CREATE TABLE IF NOT EXISTS users(
                           user_id INTEGER,
                           shop_id TEXT
                           )
                           ''')
        
        await conn.execute('''
                        CREATE TABLE IF NOT EXISTS products(
                           shop_id TEXT NOT NULL,
                           cod INTEGER,
                           data TEXT,
                           name_product TEXT,
                           FOREIGN KEY (shop_id) REFERENCES users (shop_id) ON DELETE CASCADE)
                           ''')
        await conn.commit()
    
asyncio.run(main())
