from vk_folder.bot import Bot
import os

import threading

token = os.getenv('token_user')

if __name__ == '__main__':
    bot = Bot(token)
    thr_qr_code = threading.Thread(name='bot_code', target=bot.start_run())
    thr_qr_code.start()

    # bot.start_run()