import asyncio
import logging

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import load_config
from aiogram import Bot, Dispatcher
from handlers import user_handlers


config = load_config()
BOT_TOKEN = config.tg_bot.token
ADMIN_IDS = config.tg_bot.admin_ids
PRIMARY_KEYS = config.tg_bot.PRIMARY_KEYS
bot = Bot(BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



logger = logging.getLogger(__name__) 

logger.setLevel(10)
handler = logging.FileHandler('my_log.log', 'a', encoding='utf-8')
formatter = logging.Formatter('[{asctime}] #{levelname} {filename}:{lineno} - {message}', style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def main():
    dp.include_router(user_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)
    logger.info('start polling')

if __name__ == '__main__':
    asyncio.run(main())