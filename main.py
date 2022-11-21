from vk_folder.bot import Bot
import os

token = os.getenv('token')

if __name__ == '__main__':
    bot = Bot(token)
    bot.start_run()