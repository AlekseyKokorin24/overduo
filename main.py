import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, Redis
from config_data.config import load_config
from aiogram import Bot, Dispatcher
from handlers import user_handlers
from aiogram.types import BotCommand

import sqlite3

def connection():
    conn =sqlite3.connect('overduo.db')
    cursor = conn.execute('SELECT shop_id FROM users')
    cursor = cursor.fetchall()
    PRIMARY_KEYS = set()
    for i in cursor:
        PRIMARY_KEYS.add(i[0])
    return PRIMARY_KEYS

config = load_config()

BOT_TOKEN = config.tg_bot.token
ADMIN_IDS = config.tg_bot.admin_ids
PRIMARY_KEYS = connection()
redis = Redis(host='localhost')
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)


logger = logging.getLogger(__name__) 

logger.setLevel(10)
handler = logging.FileHandler('my_log.log', 'a', encoding='utf-8')
formatter = logging.Formatter('[{asctime}] #{levelname} {filename}:{lineno} - {message}', style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запускаем бота')
    ]

    await bot.set_my_commands(main_menu_commands)
    
async def main():
    dp.include_router(user_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(set_main_menu)
    await dp.start_polling(bot) 
    logger.info('start polling')

if __name__ == '__main__':
    logger.info('start polling')
    asyncio.run(main())