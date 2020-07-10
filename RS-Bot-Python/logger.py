import discord, discord.utils as utils
import logging
import asyncio
import sys
import config as cfg

class CustomLogger(logging.Logger):
    def __init__(self,name,*args,log_fname="log.txt",bot=None,**kwargs):
        super().__init__(name,*args,level=logging.INFO,**kwargs)

        self.file_formatter = logging.Formatter(
            "[%(asctime)s | %(module)s | %(lineno)s | %(levelname)s] - %(message)s"
            )
        self.stream_formatter = logging.Formatter(
            "\033[93m[%(asctime)s] %(levelname)s: %(message)s\033[0m"
            )
        
        self.file_handler = logging.FileHandler(cfg.DIR_PATH + log_fname)
        self.file_handler.setLevel(logging.WARNING)
        self.file_handler.setFormatter(self.file_formatter)

        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(self.stream_formatter)

        self.addHandler(self.file_handler)
        self.addHandler(self.stream_handler)

        if bot:
            self.bot = bot
            self.bot_handler = BotHandler(self.bot)
            self.bot_handler.setFormatter(self.file_formatter)
            self.addHandler(self.bot_handler)

class BotHandler(logging.Handler):
    def __init__(self,bot,*args,**kwargs):
        super().__init__(*args,level=logging.INFO,**kwargs)
        self.bot = bot

    def handle(self,record):
        server = utils.get(self.bot.servers,id=cfg.SERVER_ID)
        channel = utils.get(server.channels,id=cfg.BOTLOG_ID)
        
if __name__ == "__main__":
    try:
        l = CustomLogger("testlogger")
        l.error("test error")
        l.warning("test warning")
        l.info("test info")
    finally:
        for h in l.handlers:
            h.close()
            l.removeHandler(h)

    
