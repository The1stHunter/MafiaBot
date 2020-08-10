from player import Player
import roles
from random import shuffle


class Game:
    """Класс игры в Мафию"""
    # Возможные состояния чата
    conditions = ['Registration', 'Vote', 'Mafia', 'Sheriff']

    def __init__(self, chat_id: int,):
        self.id = chat_id  # Id чата в котором проходит игра
        self.players = []  # Список игроков класса Player
        self.condition = 'Registration'  # Состояние игры
        self.index_condition = 0  # Индекс состояния
        self.round = 0  # Номер текущего круга
        self.alive_players = []  # Список живых людей
        self.winner = ''  # Победившая в игре команда
        self.killed = None  # Убитый ночью или в хоже голосования человек

    def next_condition(self):
        """Переход игры в следующее состояние
        Возвращает фразу, которую говорит бот"""
        phrase = ''
        # Если переходим из голосования, все счётчики для голосования обнуляются
        if self.condition == 'Vote':
            for player in self.players:
                player.vote = 0
                player.votes_count = 0
            # Проводим конец голосования
            self.end_vote()
            if self.killed:
                phrase = f'По Итогу голосования убит(а) {self.get_name_by_id(self.killed)}.'
            else:
                phrase = 'По итогу голосования никто не убит.'
            # После голосования проводим проверку победы
            if self.check_end_game():
                phrase += f'Стоп-игра! {self.winner}'
            else:
                phrase += '\nВ городе ночь.'
            self.killed = None  # После оглашения последнего убитого обнуляем эти данные
        elif self.condition == 'Sheriff':
            # Оглашаем ночное убийство
            phrase = f'В городе утро. Утро не доброе. Убит(а) {self.get_name_by_id(self.killed)}'
            self.killed = None
            # Проводим проверку победы
            if self.check_end_game():
                phrase += f'Стоп-игра! {self.winner}'
        elif self.condition == 'Registration':
            self.get_roles()
            phrase = 'Регистрация завершена! Напишите мне в личку /role чтобы узнать свои роли (Моя личка ' \
                     'https://t.me/TFH_mafia_bot) И приступайте к обсуждению.'
        # Зацикливание переходов
        if self.index_condition == 3:
            self.index_condition = 1
            self.round += 1
        else:
            self.index_condition += 1
        self.condition = Game.conditions[self.index_condition]
        return phrase

    def get_roles(self):
        """Получение ролей"""
        assert self.index_condition == 0, 'Incorrect condition'  # Получение ролей возможно только после регистрации
        assert roles.minimum <= len(self.players) <= roles.maximum, 'Incorrect count of players'  # Проверка количества игроков
        roles_list = roles.roles[str(len(self.players))]
        shuffle(roles_list)
        for player, role in zip(self.players, roles_list):
            player.role = role  # Роль
            player.alive = 1  # Статус жизни (1 - жив, 0 - убит)
            player.vote = 0  # Статус голосования (1 - голосовалб 0 - не голосовал)
            player.votes_count = 0  # Количетсво голосов против этого игрока

    def add_player(self, player: Player):
        """Добавление пользователя"""
        assert self.condition == Game.conditions[0], 'Can add player only in Registration'
        self.players.append(player)
        self.alive_players.append(player)

    def kill(self, player_id: int):
        """Убийство игрока"""
        self.killed = player_id
        # Смена статуса жизни на 0
        for player in self.players:
            if player.id == player_id:
                player.alive = 0
                break
        # Убираем из списка живых
        for i in range(len(self.alive_players)):
            if self.alive_players[i].id == player_id:
                self.alive_players.pop(i)
                return

    def vote(self, player_id: int, vote_id: int):
        """Голосование за игрока player_id - за кого голосуют
        vote_id - кто голосует"""
        for player in self.players:
            if player.id == vote_id:
                if player.vote == 1:
                    raise Exception  # Игрок голосует только 1 раз
                else:
                    player.vote = 1
                    break
        for player in self.players:
            if player.id == player_id:
                player.votes_count += 1
                return

    def check_end_game(self):
        """Проверяет продолжится ли игра или нет"""
        black_count = red_count = 0
        for player in self.players:
            if player.role in [roles.mafia, roles.don]:
                black_count += 1
            else:
                red_count += 1
        if black_count >= red_count:
            self.winner = 'Победила мафия'
            return True
        elif black_count == 0:
            self.winner = 'Победил город'
            return True
        return False

    def end_vote(self):
        """Подсчёт итога голосования"""
        max_vote = 0  # Максимальное число голов за игрока
        count_vote = 1  # Количество таких игроков
        player_id = self.players[0].id  # Id одного из них
        for player in self.players:
            if player.votes_count == max_vote:
                count_vote += 1
            if player.votes_count > max_vote:
                max_vote = player.votes_count
                count_vote = 1
                player_id = player.id
        # Если человек с максимальным количеством голосов 1 - убиваем его
        if count_vote == 1:
            self.kill(player_id)

    def get_role_by_id(self, player_id: int):
        """Получение роли по id"""
        for player in self.players:
            if player.id == player_id:
                return player.role

    def get_name_by_id(self, player_id: int):
        """Получение имени по id"""
        for player in self.players:
            if player.id == player_id:
                return f'{player.first_name} {player.last_name}'
