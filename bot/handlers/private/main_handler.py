from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Order
from db import User

main_router = Router()


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_data = message.from_user.model_dump(include={'id', 'first_name', 'username'})
    if not await User.get(message.from_user.id):
        await User.create(**user_data)

    rkm = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📚 Kitoblar")],
        [KeyboardButton(text="📃 Mening buyurtmalarim")],
        [KeyboardButton(text="🔵 Biz ijtimoiy tarmoqlarda"), KeyboardButton(text="📞 Biz bilan bog'lanish")]
    ],
        resize_keyboard=True,
    )
    await message.answer("Assalomu alaykum! Tanlang.", reply_markup=rkm)


@main_router.message(F.text == "📞 Biz bilan bog'lanish")
async def contact(message: Message):
    await message.answer(f'''
Telegram: @factorbooks_info

📞 + 998908263202

🤖 Bot Makhmudov Doniyor (@theHonoredOne66) tomonidan tayyorlandi.
    
    ''')


@main_router.message(F.text == '📃 Mening buyurtmalarim')
async def order_handler(message: Message):
    orders = await Order.get_all()
    if orders:
        for order in orders:
            await message.answer(f'''
Your orders:
Name: {order.product}
Price: {order.quantity}
''')
    else:
        await message.answer('🤷‍♂️ Sizda xali buyurtmalar mavjud emas.')

