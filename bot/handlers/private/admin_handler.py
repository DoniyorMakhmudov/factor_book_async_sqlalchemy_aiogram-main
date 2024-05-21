from aiogram import Router
from aiogram.types import Message

from bot.filters.is_admin_filter import IsAdminFilter

admin_router = Router()


@admin_router.message(IsAdminFilter())
async def command_start_handler(message: Message) -> None:
    await message.answer('Siz adminsiz')
