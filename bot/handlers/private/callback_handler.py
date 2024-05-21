from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import conf
from db import Product, Category, Order

callback_router = Router()

class Form(StatesGroup):
    quantity = State()

# Function to create the product selection keyboard
def create_product_selection_keyboard(products):
    ikb = InlineKeyboardBuilder()
    for product in products:
        ikb.add(InlineKeyboardButton(text=product.name, callback_data=f'product_{product.id}'))
    ikb.adjust(2, repeat=True)
    return ikb

# Function to create the product detail keyboard
def create_product_detail_keyboard(quantity):
    kb = InlineKeyboardBuilder()
    kb.button(text='➖', callback_data='decrease')
    kb.button(text=str(quantity), callback_data='info')
    kb.button(text='➕', callback_data='increase')
    kb.button(text='◀️ Orqaga', callback_data='go_back')
    kb.button(text="🛒 Savatga qo'shish", callback_data='add_to_basket')
    kb.adjust(3, 2, repeat=True)
    return kb

@callback_router.callback_query(F.data.startswith('category_'))
async def category_callback_handler(callback: CallbackQuery) -> None:
    category_id = int(callback.data.split('category_')[-1])
    products = await Product.get_products_by_category_id(category_id)
    ikb = create_product_selection_keyboard(products)

    await callback.message.edit_text('Productni tanlang 📚', reply_markup=ikb.as_markup())

@callback_router.callback_query(F.data.startswith('product_'))
async def product_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.quantity)

    product_id = int(callback.data.split('product_')[-1])
    product = await Product.get(product_id)
    quantity = 1  # Initial quantity

    # Store the product ID, category ID, and initial quantity in the state
    await state.update_data(quantity=quantity, product_id=product_id, category_id=product.category_id)

    context = f'''
🔹 Nomi: {product.name}
Qoshimcha ma'lumot: {product.description}
💸 Narxi: {product.price}
'''
    kb = create_product_detail_keyboard(quantity)

    await callback.message.delete()
    await callback.message.answer_photo(photo=URLInputFile(product.photo.telegra_image_url), caption=context, reply_markup=kb.as_markup())

@callback_router.callback_query(F.data.in_({'decrease', 'increase'}))
async def process_quantity_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get('quantity', 1)  # Retrieve the current quantity
    product_id = data.get('product_id')  # Retrieve the stored product ID

    if callback.data == 'decrease':
        if quantity > 1:
            quantity -= 1
    elif callback.data == 'increase':
        quantity += 1

    # Update the quantity in the state
    await state.update_data(quantity=quantity)

    product = await Product.get(product_id)
    context = f'''
🔹 Nomi: {product.name}
Qoshimcha ma'lumot: {product.description}
💸 Narxi: {product.price}
'''
    kb = create_product_detail_keyboard(quantity)

    await callback.message.edit_caption(caption=context, reply_markup=kb.as_markup())

@callback_router.callback_query(F.data == 'go_back')
async def process_go_back(callback: CallbackQuery):
    await callback.message.delete()
    categories = await Category.get_all()  # Assuming you have a method to get all categories
    ikb = InlineKeyboardBuilder()
    for category in categories:
        ikb.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    ikb.adjust(2, repeat=True)
    await callback.message.answer('Kategoriyani tanlang:', reply_markup=ikb.as_markup())

@callback_router.callback_query(F.data == 'add_to_basket')
async def add_to_basket_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get('quantity', 1)
    product_id = data.get('product_id')
    category_id = data.get('category_id')
    user_id = callback.from_user.id  # Assuming the user's Telegram ID is used as the user_id

    # Create a new order
    await Order.create(user_id=user_id, category_id=category_id, product_id=product_id, quantity=quantity)

    await callback.message.delete()
    await callback.answer('🛒Savatga qoshildi 😊', show_alert=True)

    categories = await Category.get_all()
    ikb = InlineKeyboardBuilder()
    orders = await Order.get_all()
    quantity_of_order = sum(1 for order in orders if order.user_id == user_id)

    for category in categories:
        ikb.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    ikb.add(InlineKeyboardButton(text='🔍Qidirish', callback_data='search'),
            InlineKeyboardButton(text=f'🛒Savat ({quantity_of_order})', callback_data='quantity_of_order'))
    ikb.adjust(2, repeat=True)
    await callback.message.answer('Kategoriyani tanlang:', reply_markup=ikb.as_markup())

@callback_router.callback_query(F.data.startswith('quantity_of_order'))
async def quantity_of_order_handler(callback: CallbackQuery, state:FSMContext):
    user_id = callback.from_user.id
    total_price = 0
    ikb = InlineKeyboardBuilder()
    ikb.add(
        InlineKeyboardButton(text='❌ Savatni tozalash', callback_data='order_delete'),
        InlineKeyboardButton(text='✅ Buyurtmani tasdiqlash', callback_data='order_create'),
        InlineKeyboardButton(text='◀️ Orqaga', callback_data='go_back'),
    )
    ikb.adjust(1, repeat=True)

    text = "🛒 Savat\n\n"

    orders = await Order.get_all()
    for order in orders:
        if order.user_id == user_id:
            product = await Product.get(order.product_id)
            total_price += product.price * order.quantity
            text += f"{product.name}\n{order.quantity} x {product.price} = {product.price * order.quantity}\n\n"
    text += f"Jami: {total_price} so'm"

    # Store the cart text in the state for later use
    await callback.message.answer(text, reply_markup=ikb.as_markup())
    await state.update_data(cart_text=text)

@callback_router.callback_query(F.data.startswith('order'))
async def order_handler(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    order_info = callback_query.data.split('order_')[-1]
    user_id = callback_query.from_user.id
    orders = await Order.get_all()
    order_ids = [order.id for order in orders if order.user_id == user_id]

    if order_info == 'delete':
        for order_id in order_ids:
            await Order.delete(order_id)

        await callback_query.message.delete()
        await callback_query.answer('🛒 Savat tozalandi', show_alert=True)
    elif order_info == 'create':
        data = await state.get_data()
        cart_text = data.get('cart_text', 'Buyurtma ma\'lumotlari mavjud emas')

        # Assuming ADMIN is defined with the chat ID of the admin
        await bot.send_message(chat_id=conf.ADMIN_LIST, text=cart_text)

        # Clear the user's orders after sending the order details
        for order_id in order_ids:
            await Order.delete(order_id)

        await callback_query.message.delete()
        await callback_query.answer('✅ Buyurtma tasdiqlandi', show_alert=True)
