"""Здесь код бота. Библиотека pyTelegramBotAPI"""
import telebot
from config import token
bot = telebot.TeleBot(token)
import utils as dbu
from telebot import types


@bot.message_handler(commands=['vote'])
def vote(message:telebot.types.Message):
    """Голосование"""
    if message.from_user.id == message.chat.id:
        """Личная переписка с ботом"""

    else:
        """Групповая переписка с ботом"""
        keyboard = types.InlineKeyboardButton()
        all_players = dbu.get_players_info_chat(message.chat.id)
        for player in all_players:
            if player[6] == 1:
                name = types.InlineKeyboardButton(text=f'{player[1]} {player[2]}',callback_data=player[0])
                keyboard.add(name)
        bot.send_message(message.chat.id,text='Голосование',reply_markup=keyboard)


# @bot.message_handler(content_types=['text'])
# def answer(message:telebot.types.Message):
#     player_info = dbu.get_player_info(message.chat.id)
#
#     if dbu.work_with_db(dbu.check_chat_status, player_info[3], ["Vote"]):
#         message = message.split(" ")
#         try:
#             chat_info = dbu.get_players_info_chat(player_info[3])
#             if chat_info[1].index(player_info[1]) == chat_info[2].index(player_info[2]):
#                 """Продолжение если игрок найден в списке игроков группы"""
#
#         except:
#             """Продолжение если игрок НЕ найден в списке игроков группы"""
#             bot.send_message(message.chat.id,"Такого игрока не существует, попробуй еще раз. Напиши /vote")


@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    all_players = dbu.get_players_info_chat(call.message.chat.id)
    for player in all_players:
        if call.data == player[0]:
            player["""Id для подчета голосов"""]+=1
