import threading
import asyncio
import bot
import tcp_echo

loop = asyncio.get_event_loop()

bot_thread = threading.Thread(target=lambda: bot.main(loop))
server_thread = threading.Thread(target=tcp_echo.main)

bot_thread.start()
server_thread.start()
bot_thread.join()
server_thread.join()
