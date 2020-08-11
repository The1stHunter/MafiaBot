import telebot
from config import token
import roles
import utils
from player import Player
from telebot import types

bot = telebot.TeleBot(token)
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
        game = utils.get_game(message.chat.id)
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


@bot.message_handler(commands=['kill'])
def kill(message: telebot.types.Message):
    """Убийство мафии"""
    if message.from_user.id == message.chat.id:
        """Личная переписка с ботом"""
        game = utils.get_game(utils.get_chat(message.chat.id))
        if game.condition == 'Mafia':
            player_role = game.get_role_by_id(message.chat.id)
            if player_role.color == 'black':
                keyboard = types.InlineKeyboardMarkup()
                all_players = game.alive_players
                for p in all_players:
                    name = types.InlineKeyboardButton(text=f'{p.first_name} {p.last_name}', callback_data=p.id)
                    keyboard.add(name)
                bot.send_message(message.chat.id, text='Убийство!', reply_markup=keyboard)
            else:
                bot.reply_to(message, 'Ты не мафия, не прикидывайся!')
        else:
            bot.reply_to(message, 'Сейчас не стадия мафии!')

    else:
        """Групповая переписка с ботом"""
        bot.send_message(message.chat.id, text='Не туда пишешь, дурачок')


@bot.message_handler(commands=['check'])
def check(message: telebot.types.Message):
    """Проверка шерифа"""
    if message.from_user.id == message.chat.id:
        """Личная переписка с ботом"""
        game = utils.get_game(utils.get_chat(message.chat.id))
        if game.condition == 'Sheriff':
            keyboard = types.InlineKeyboardMarkup()
            all_players = game.alive_players
            for p in all_players:
                name = types.InlineKeyboardButton(text=f'{p.first_name} {p.last_name}', callback_data=p.id)
                keyboard.add(name)
            bot.send_message(message.chat.id, text='Проверка!', reply_markup=keyboard)
        else:
            bot.reply_to(message, 'Сейчас не стадия шерифа!')
    else:
        """Групповая переписка с ботом"""
        bot.send_message(message.chat.id, text='Не туда пишешь, дурачок')


@bot.callback_query_handler(func=lambda call: utils.get_game(call.message.chat.id).condition == 'Mafia')
def mafia(call: types.CallbackQuery):
    """Обработка стадии игры Мафия"""
    game = utils.get_game(call.message.chat.id)
    player_role = game.get_role_by_id(call.message.chat.id)
    if player_role.vote == 1:
        game.kill(call.data)
        utils.set_game(utils.get_chat(call.from_user.id), game)
    elif player_role.vote == 0:
        # TODO: Если добавлять в игру третью мафию, искать придётся не по роли Дон, а по голосующей роли (vote == 1)
        # TODO: Нет самой функции get_id_by_role
        bot.send_message(game.get_id_by_role('don'), f"{game.get_name_by_id(call.message.chat.id)} советует "
                                                     f"тебе убить {game.get_name_by_id(call.data)}")
        # TODO: предлагаю такой вариант
        for player in game.alive_players:
            if player.role.color == 'Black':
                bot.send_message(player.id, f"{game.get_name_by_id(call.message.chat.id)} советует "
                                            f"убить {game.get_name_by_id(call.data)}")


@bot.callback_query_handler(func=lambda call: utils.get_game(call.message.chat.id).condition == 'Sheriff')
def sheriff(call: types.CallbackQuery):
    """Обработка стадии игры Шериф"""
    game = utils.get_game(call.message.chat.id)
    bot.send_message(call.message.chat.id,
                     f"Цвет игрока {game.get_name_by_id(call.data)} - {game.get_role_by_id(call.data).color}")


@bot.callback_query_handler(func=lambda call: utils.get_game(call.message.chat.id).condition == 'Vote')
def vote(call: types.CallbackQuery):
    """Обработка голосования"""
    # TODO: сделать так чтобы это работало в многопоточности
    game = utils.get_game(call.message.chat.id)
    # Если игрок жив, он может голосовать
    if call.from_user.id in [player.id for player in game.alive_players]:
        msg = game.vote(int(call.data), int(call.from_user.id))
        bot.send_message(call.message.chat.id, msg)
        # Если все проголосовали, переходим на следующую стадию
        if game.count_vote == len(game.players):
            msg = game.next_condition()
            bot.send_message(call.message.chat.id, msg)
        # Если игра закончилась
        if game.check_end_game():
            bot.send_message(call.message.chat.id, f'Роли были такие:\n{game.roles()}')
            # utils.end_game(call.message.chat.id)
            # utils.delete_chat(call.message.chat.id)
            pass
        utils.set_game(call.message.chat.id, game)
    # Если игрок мёртв
    else:
        bot.send_message(call.message.chat.id, f'{game.get_name_by_id(call.from_user.id)}, мёртвые не голосуют!')


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
