import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler
from aiohttp import web

from bot.handlers import private_handler_router
from config import conf
from db import database


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await database.create_all()
    # await bot.set_webhook(f"{conf.bot.BASE_WEBHOOK_URL}{conf.bot.WEBHOOK_PATH}", secret_token=conf.bot.WEBHOOK_SECRET)


async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    pass
    # await bot.delete_webhook(drop_pending_updates=True)


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(private_handler_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    bot = Bot(token=conf.bot.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Create aiohttp.web.Application instance
    await dp.start_polling(bot)
    #
    # app = web.Application()
    #
    # # Create an instance of request handler,
    # # aiogram has few implementations for different cases of usage
    # # In this example we use SimpleRequestHandler which is designed to handle simple cases
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=conf.bot.WEBHOOK_SECRET
    # )
    # # Register webhook handler on application
    # webhook_requests_handler.register(app, path=conf.bot.WEBHOOK_PATH)
    #
    # # Mount dispatcher startup and shutdown hooks to aiohttp application
    # setup_application(app, dp, bot=bot)
    #
    # # And finally start webserver
    # web.run_app(app, host=conf.bot.WEB_SERVER_HOST, port=conf.bot.WEB_SERVER_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
