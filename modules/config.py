import telebot
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = telebot.TeleBot(TOKEN)
