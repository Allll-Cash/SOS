import os

import telebot
from django.core.management import BaseCommand
from telebot.types import Message

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))


@bot.message_handler(content_types=[
    'audio',
    'photo',
    'voice',
    'video',
    'document',
    'text',
    'location',
    'contact',
    'sticker'
])
def handle(message: Message):
    from bot.bot_core import Core
    Core(message).process()


class Command(BaseCommand):

    def handle(self, *args, **options):
        bot.polling()
