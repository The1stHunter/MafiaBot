import telebot
from config import token
import roles
import db_utils as dbu
import shelves_utils as shu
from db_utils import work_with_db


bot = telebot.TeleBot(token)
start_message = """Привет! Я ведущий игры в мафию.
Для начала регистрации введите /startreg
Затем каждый участник вводит /regme
Когда все желающие зарегестрированны пишите /endreg
А потом напишите мне в личку /role, и я скажу вам ваши роли. 
Удачи!"""
start_message_one = f"""Привет! Я ведущий игры в мафию.
Создай группу из {roles.minimum} - {roles.maximum} игроков,
пригласи меня туда и я помогу вам провести игру."""


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    """Приветствие"""
    # В личке
    if message.from_user.id == message.chat.id:
        bot.send_message(message.chat.id, start_message_one)
    # В группе
    else:
        bot.send_message(message.chat.id, start_message)


@bot.message_handler(commands=['startreg'])
def startreg(message: telebot.types.Message):
    """Начало регистрации"""
    # В группе
    if message.from_user.id != message.chat.id:
        # Если чат не играет
        if not work_with_db(dbu.chat_in_game, message.chat.id):
            shu.start(message.chat.id)
            work_with_db(dbu.start, message.chat.id)
            bot.send_message(message.chat.id, """Объявляю начало регистрации
Пишите /reg чтобы я добавил вас в игру
Пишите /endreg когда все желающие зарегистрировались""")


@bot.message_handler(commands=['reg'])
def reg(message: telebot.types.Message):
    # В группе
    if message.from_user.id != message.chat.id:
        # Если статус чата Регистрация
        if work_with_db(dbu.check_chat_status, message.chat.id, ['Registration']):
            # Проверка нахождения пользователя в другой игре
            if work_with_db(dbu.user_in_game, message.from_user.id):
                bot.reply_to(message, 'Вы находитесь в другой игре')
            elif shu.user_in_game(message.chat.id, message.from_user.id):
                bot.reply_to(message, 'Вы уже зарегестрированы')
            else:
                shu.register_user(message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.last_name)
                bot.reply_to(message, 'Вы успешно зарегестрированы')


@bot.message_handler(commands=['endreg'])
def endreg(message: telebot.types.Message):
    """Конец регистрации в чате"""
    # В группе
    if message.from_user.id != message.chat.id:
        # Если статус чата Регистрация
        if work_with_db(dbu.check_chat_status, message.chat.id, ['Registration']):
            # Провека количества игроков
            players_count = shu.players_count(message.chat.id)
            if roles.minimum <= players_count <= roles.maximum:
                # Получаем роли
                work_with_db(dbu.set_chat_status, message.chat.id, 'GetRole')
                work_with_db(dbu.reg_users, message.chat.id)
                bot.send_message(message.chat.id, """Регистрация окончена! 
Пишите мне в личку /role
(Моя личка https://t.me/TFH_mafia_bot)""")
            else:
                bot.send_message(message.chat.id, f"""Похоже у нас проблемы с количеством(
Я могу провести игру только для {roles.minimum}-{roles.maximum} человек""")


@bot.message_handler(commands=['role'])
def role(message):
    # В личке
    if message.from_user.id == message.chat.id:
        # Если человек играет:
        if work_with_db(dbu.user_in_game, message.chat.id):
            # Отправляем ему его роль
            player_role = work_with_db(dbu.get_players_info, message.chat.id)[4]
            bot.send_message(message.chat.id, f'Ты - {player_role}!')
            # Меняем статус игрока на Получил роль
            work_with_db(dbu.change_players_info, message.chat.id, 'Game_status', 'GetRole')
            # Если все игроки получили роли начинается Обсуждение
            # TODO: сделать


@bot.message_handler(commands=['endgame'])
def endgame(message: telebot.types.Message):
    """Принудительное завершение игры"""
    shu.delete_info(message.chat.id)
    work_with_db(dbu.delete_chat, message.chat.id)
    bot.send_message(message.chat.id, 'Игра окончена')


if __name__ == '__main__':
    bot.infinity_polling()
