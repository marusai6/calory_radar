import asyncio
from aiogram import Bot, Dispatcher
import configparser
import logging
from aiogram.client.default import DefaultBotProperties
from handlers.user import message


config = configparser.ConfigParser()
config.read('./config/config.ini')

logger = logging.getLogger(__name__)


async def main():
    token = config['Telegram']['token']
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    
    bot = Bot(token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(message.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())