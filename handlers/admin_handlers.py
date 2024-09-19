from filters import IsAdmin
from aiogram import Router
from aiogram.types import Message
from other_func import connect


router = Router()


@router.message(IsAdmin(Message.from_user.id))
async def send_info_about_overduo(message: Message):
    await connect(typeActions='send_overduo_message_TA')