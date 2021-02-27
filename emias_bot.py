from bot import Bot

with open('token.txt') as fin:
    TOKEN = fin.read().strip()

bot = Bot(TOKEN, "./emias_buff.csv")

bot.loop()