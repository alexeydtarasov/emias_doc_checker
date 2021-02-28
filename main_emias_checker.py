from bot import Bot

from traceback import format_exc

with open('token.txt') as fin:
    TOKEN = fin.read().strip()

bot = Bot(TOKEN, "./emias_buff.csv")

try:
    bot.loop()
except:
    bot.send_error_alert(format_exc)