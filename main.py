import telebot
from config import token
import roles
import utils
from game import Game
from player import Player
from telebot import types
import time

# TODO: переход с Дона на мертвого Шерифа
# TODO: команды после регистрации не должны класть бота (kill, vote...)
# TODO: правильные ответы игроку после смерти
# TODO: показывать роли в конце игры при победе мафии после ночи


bot = telebot.TeleBot(token)


def kill(game: Game):
    """Убийство"""
    keyboard = types.InlineKeyboardMarkup()
    all_players = game.alive_players
    for p in all_players:
        name = types.InlineKeyboardButton(text=f'{p.first_name} {p.last_name}', callback_data=p.id)
        keyboard.add(name)
    for player in [player.id for player in game.black_alive_players]:
        bot.send_message(player, game.alive_mates_names(player))
        bot.send_message(player, text='Убийство! У вас 60 секунд, чтобы сделать свой выбор',
                         reply_markup=keyboard)

    utils.set_game(game.id, game)
    # Таймер на 60 секунд
    time.sleep(60)
    # Перезапись игры с записью убийства (которое в колбеках делается)
    game = utils.get_game(game.id)
    msg = game.next_condition()
    # Если игра не переключилось на состояние Дона (мафия не сделал убийство), идём на следующее состояние ещё раз
    if game.condition == 'EndMafia':
        msg = game.next_condition()
    # Запись нового состояния
    utils.set_game(game.id, game)
    bot.send_message(game.id, msg)

    # Переход к жругой стадии
    check_don(game)


def check_don(game: Game):
    """Проверка дона"""
    keyboard = types.InlineKeyboardMarkup()
    all_players = game.players
    for p in all_players:
        name = types.InlineKeyboardButton(text=f'{p.first_name} {p.last_name}', callback_data=p.id)
        keyboard.add(name)
    bot.send_message(game.don.id, text='Игра! Угадай кто шериф. У тебя 60 секунд.',
                     reply_markup=keyboard)

    # Таймер на 60 секунд
    time.sleep(60)
    game = utils.get_game(game.id)
    msg = game.next_condition()
    if game.condition == 'EndDon':
        msg = game.next_condition()
    bot.send_message(game.id, msg)
    utils.set_game(game.id, game)
    # Переход к жругой стадии
    check_sheriff(game)


def check_sheriff(game: Game):
    """Проверка шерифа"""
    keyboard = types.InlineKeyboardMarkup()
    all_players = game.players
    for p in all_players:
        name = types.InlineKeyboardButton(text=f'{p.first_name} {p.last_name}', callback_data=p.id)
        keyboard.add(name)
    bot.send_message(game.sheriff.id, text='Игра! Угадай кто мафия. У тебя 60 сек', reply_markup=keyboard)

    # Таймер на 60 секунд
    time.sleep(60)
    game = utils.get_game(game.id)
    msg = game.next_condition()
    if game.condition == 'EndSheriff':
        msg = game.next_condition()
    bot.send_message(game.id, msg)
    utils.set_game(game.id, game)

    if game.check_end_game():
        bot.send_message(game.id, f'Роли были такие:\n{game.roles()}')
        # utils.end_game(call.message.chat.id)
        # utils.delete_chat(call.message.chat.id)


start_message = """Привет! Я ведущий игры в мафию.
Для начала каждый участник вводит /reg
Когда все желающие зарегестрированны пишите /endreg
А потом напишите мне в личку /role, и я скажу вам ваши роли. 
Удачи!"""
start_message_one = f"""Привет! Я ведущий игры в мафию.
Создай группу из {roles.minimum} - {roles.maximum} игроков,
пригласи меня туда и я помогу вам провести игру."""


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    """Приветствие"""
    if message.from_user.id == message.chat.id:
        bot.send_message(message.chat.id, start_message_one)
    else:
        bot.send_message(message.chat.id, start_message)


@bot.message_handler(commands=['reg'])
def reg_me(message: telebot.types.Message):
    """Регистрация пользователя"""
    if message.from_user.id == message.chat.id:
        bot.send_message(message.chat.id, 'Напиши это из группы, чтобы я тебе зарегестрировал')
    else:
        if utils.check_player(message.from_user.id):
            if utils.get_chat(message.from_user.id) == str(message.chat.id):
                bot.reply_to(message, 'Вы уже зарегестрированы')
            else:
                bot.reply_to(message, 'Вы уже участвуете в другой игре')
        else:
            utils.add_row(message.from_user.id, message.chat.id, message.from_user.first_name,
                          message.from_user.last_name)
            bot.reply_to(message, 'Вы зарегестрированы!')


@bot.message_handler(commands=['endreg'])
def end_reg(message: telebot.types.Message):
    """Конец регистрации"""
    # В личке
    if message.from_user.id == message.chat.id:
        bot.send_message(message.chat.id, 'Эта команда работает только в группе')
    # В группе
    else:
        if utils.count_players(message.chat.id) < roles.minimum:
            bot.reply_to(message,
                         f'Похоже, вас слишком мало для игры в мафию. Необходимо хотя бы {roles.minimum} человека.')
        elif utils.count_players(message.chat.id) > roles.maximum:
            bot.reply_to(message,
                         f'Похоже, вас слишком много, я могу провести игру максимум для {roles.maximum} людей.')
        else:
            try:
                game = utils.get_game(message.chat.id)
            except KeyError:
                # Если стадия игры - Регистрация (хранилище с игрой ьудет созданно только сейчас, поэтому при
                # регистрациии должна появляться ошибка KeyError
                msg = utils.start_game(message.chat.id, utils.get_players_info(message.chat.id))
                for player in utils.get_players(message.chat.id):
                    utils.change_role_status(player, '2')
                bot.send_message(message.chat.id, msg)
            else:
                bot.send_message(message.chat.id, 'Регистрация уже окончена.')


@bot.message_handler(commands=['role'])
def role(message: telebot.types.Message):
    """Выдача роли"""
    if message.from_user.id == message.chat.id:
        if utils.get_role_status(message.from_user.id) == '1':
            bot.send_message(message.from_user.id, 'Твоя роль ещё не готова. Подожди пока все игроки зарегестрируются.')
        elif utils.get_role_status(message.from_user.id) == '2':
            chat = utils.get_chat(message.from_user.id)
            game = utils.get_game(chat)
            bot.send_message(message.from_user.id, f'Ты - {game.get_role_by_id(message.from_user.id)}!')
            # Если игрок мафия - прислать ему список его союзников
            if message.from_user.id in [player.id for player in game.black_alive_players]:
                bot.send_message(message.chat.id, game.alive_mates_names(message.from_user.id))
            utils.change_role_status(message.from_user.id, '3')
            # Если это был последний получивший роль - переходим на следующую стадию
            if utils.get_count_ready_role(chat) == len(game.players):
                msg = game.next_condition()
                utils.set_game(chat, game)
                bot.send_message(chat, msg)

        elif utils.get_role_status(message.from_user.id) == '3':
            chat = utils.get_chat(message.from_user.id)
            game = utils.get_game(chat)
            bot.send_message(message.from_user.id,
                             f'Повторяю, ты - {game.get_role_by_id(message.from_user.id)}!')
            # Если игрок мафия - прислать ему список его союзников
            if message.from_user.id in [player.id for player in game.black_alive_players]:
                bot.send_message(message.chat.id, game.alive_mates_names(message.from_user.id))

        else:
            print('Твоя бд сломана!!!')
    else:
        bot.reply_to(message, 'Напиши мне это в личку')


@bot.message_handler(commands=['vote'])
def vote(message: telebot.types.Message):
    """Голосование"""
    if message.from_user.id == message.chat.id:
        """Личная переписка с ботом"""
        pass
    else:
        """Групповая переписка с ботом"""
        try:
            game = utils.get_game(message.chat.id)
        except KeyError:
            # Если игра ещё не создана
            bot.reply_to(message, 'Вы ещё не начали игру!')
            return
        # Проверяем, что стадия игры голосование
        if game.condition == 'Vote':
            keyboard = types.InlineKeyboardMarkup()
            all_players = game.alive_players
            for player in all_players:
                name = types.InlineKeyboardButton(text=f'{player.first_name} {player.last_name}',
                                                  callback_data=player.id)
                keyboard.add(name)
            bot.send_message(message.chat.id, text='Голосование!', reply_markup=keyboard)
        else:
            bot.reply_to(message, 'Сейчас не стадия голосования!')


@bot.callback_query_handler(func=lambda call: True)
def callback(call: types.CallbackQuery):
    game = utils.get_game(utils.get_chat(call.from_user.id))

    if game.condition == 'Mafia':
        """Обработка стадии игры Мафия"""
        # Если колбек пришёл от мафии
        if call.from_user.id in [player.id for player in game.black_alive_players]:
            player_role = game.get_role_by_id(call.message.chat.id)
            if player_role.vote == 1:
                game.killed = int(call.data)
                game.next_condition()
                # Отсылаем кого убили всем живым мафиям
                for player in game.black_alive_players:
                    # Кроме себя
                    if player.id != call.from_user.id:
                        bot.send_message(player.id, f"{game.get_name_by_id(call.message.chat.id)} "
                                                    f"убил {game.get_name_by_id(int(call.data))}")
                    # Себе отсылаем кого убили
                    else:
                        bot.send_message(player.id, f"Вы "
                                                    f"убили {game.get_name_by_id(int(call.data))}")
                utils.set_game(utils.get_chat(call.from_user.id), game)
            elif player_role.vote == 0:
                # Отсылаем своё мнение всем другим мафиям
                for player in game.black_alive_players:
                    # Кроме себя
                    if player.id != call.from_user.id:
                        bot.send_message(player.id, f"{game.get_name_by_id(call.message.chat.id)} советует "
                                                    f"убить {game.get_name_by_id(int(call.data))}")

                    # Себе отсылаем такое сообщение
                    else:
                        bot.send_message(player.id, f"Вы предложили "
                                                    f"убить {game.get_name_by_id(int(call.data))}")

    elif game.condition == 'Sheriff':
        """Обработка стадии игры Шериф"""
        # Если колбек пришёл от живого шерифа:
        if call.from_user.id == game.sheriff.id and call.from_user.id in [player.id for player in game.alive_players]:
            bot.send_message(call.message.chat.id,
                             f"Цвет игрока {game.get_name_by_id(int(call.data))} - {game.get_role_by_id(int(call.data)).color}")
            game.next_condition()
            utils.set_game(utils.get_chat(call.message.chat.id), game)

    elif game.condition == 'Don':
        """Обработка стадии игры Дон"""
        # Если колбек пришёл от живого дона:
        if call.from_user.id == game.don.id and call.from_user.id in [player.id for player in game.alive_players]:
            if int(call.data) == game.sheriff.id:
                bot.send_message(call.message.chat.id,
                                 f"Да, {game.get_name_by_id(int(call.data))} - Шериф!")
            else:
                bot.send_message(call.message.chat.id, f'Не-а, {game.get_name_by_id(int(call.data))} - не Шериф!')
            game.next_condition()
            utils.set_game(utils.get_chat(call.message.chat.id), game)

    elif game.condition == 'Vote':
        """Обработка голосования"""
        # TODO: сделать так чтобы это работало в многопоточности
        # Голосовать можно только в чате
        if call.from_user.id != call.message.chat.id:

            # Если игрок жив, он может голосовать
            if call.from_user.id in [player.id for player in game.alive_players]:
                msg = game.vote(int(call.data), int(call.from_user.id))
                bot.send_message(call.message.chat.id, msg)
                # Если все проголосовали, переходим на следующую стадию
                if game.count_vote == len(game.alive_players):
                    msg = game.next_condition()
                    bot.send_message(call.message.chat.id, msg)
                    utils.set_game(call.message.chat.id, game)
                    # Если игра закончилась
                    if game.check_end_game():
                        bot.send_message(call.message.chat.id, f'Роли были такие:\n{game.roles()}')
                        # utils.end_game(call.message.chat.id)
                        # utils.delete_chat(call.message.chat.id)
                        return
                    kill(game)
                else:
                    utils.set_game(call.message.chat.id, game)
            # Если игрок мёртв
            else:
                bot.send_message(call.message.chat.id,
                                 f'{game.get_name_by_id(call.from_user.id)}, мёртвые не голосуют!')


@bot.message_handler(commands=['test'])
def test(message):
    bot.reply_to(message, message.chat.id)


@bot.message_handler(commands=['endgame'])
def end_game(message: telebot.types.Message):
    utils.end_game(message.chat.id)
    utils.delete_chat(message.chat.id)
    bot.reply_to(message, 'Игра окончена!')


if __name__ == '__main__':
    bot.infinity_polling()
