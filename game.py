from player import Player
import roles
from random import shuffle


class Game:
    """Класс игры в Мафию"""
    # Возможные состояния чата
    conditions = ['Registration', 'GetRole', 'Vote', 'Mafia', 'EndMafia', 'Don', 'EndDon', 'Sheriff', 'EndSheriff']

    def __init__(self, chat_id: int, ):
        self.id = chat_id  # Id чата в котором проходит игра
        self.players = []  # Список игроков класса Player
        self.condition = 'Registration'  # Состояние игры
        self.round = 0  # Номер текущего круга
        self.winner = ''  # Победившая в игре команда
        self.killed = None  # Убитый ночью или в хоже голосования человек
        self.don_appear = 0  # Есть ли Дон и Шериф в этой игре
        self.count_vote = 0  # Количетсво проголосовавших на этом круге

    def next_condition(self):
        """Переход игры в следующее состояние
        Возвращает фразу, которую говорит бот"""
        phrase = ''
        # ГОЛОСОВАНИЕ - МАФИЯ
        # Если переходим из голосования, все счётчики для голосования обнуляются
        if self.condition == 'Vote':
            # Проводим конец голосования
            self.end_vote()
            for i in range(len(self.players)):
                self.players[i].vote = 0
                self.players[i].votes_count = 0
            self.count_vote = 0
            if self.killed:
                self.kill()
                phrase = f'По Итогу голосования убит(а) {self.get_name_by_id(self.killed)}.\n'
            else:
                phrase = 'По итогу голосования никто не убит.\n'
            # После голосования проводим проверку победы
            if self.check_end_game():
                phrase += f'Стоп-игра! {self.winner}'
            else:
                phrase += '\nВ городе ночь. Просыпается Мафия.\nМафия выбирает жертву убийства.'
            self.killed = None  # После оглашения последнего убитого обнуляем эти данные

        # МАФИЯ - ДОН
        elif self.condition == 'EndMafia':
            if self.don_appear:
                phrase += 'Мафия засыпает. Просыпается Дон.\nДон выбирает игрока чтобы узнать, является ли игрок ' \
                          'Шерифом. '

        # ДОН - ШЕРИФ
        elif self.condition == 'EndDon':
            if self.don_appear:
                phrase += 'Дон Засыпает. Просыпается Шериф.\nШериф выбирает игрока чтобы узнать, является ли ' \
                          'игрок Мафией. '

        # ШЕРИФ - ГОЛОСОВАНИЕ
        elif self.condition == 'EndSheriff':
            # Оглашаем ночное убийство
            if self.killed:
                phrase = f'В городе утро. Утро не доброе. Убит(а) {self.get_name_by_id(self.killed)}\n'
                self.kill()
            else:
                phrase += 'В городе утро. Утро доброе мафия промахнулась!\n'
            self.killed = None
            # Проводим проверку победы
            if self.check_end_game():
                phrase += f'Стоп-игра! {self.winner}'
            else:
                phrase += 'Когда будете готовы голосовать, пишите /vote'

        # РЕГИСТРАЦИЯ - ПОЛУЧЕНИЕ РОЛЕЙ
        elif self.condition == 'Registration':
            self.get_roles()
            phrase = 'Регистрация завершена! Напишите мне в личку /role чтобы узнать свои роли (Моя личка ' \
                     'https://t.me/TFH_mafia_bot) И приступайте к обсуждению.'

        # ПОЛУЧЕНИЕ РОЛЕЙ - ГОЛОСОВАНИЕ
        elif self.condition == 'GetRole':
            phrase += 'Все ирогки прочли свои роли!\nПриступайте к обсуждению, когда будете готовы голосовать, ' \
                      'напишите /vote '

        # Зацикливание переходов
        if self.condition == Game.conditions[-1]:
            self.condition = Game.conditions[2]
            self.round += 1
        else:
            self.condition = Game.conditions[Game.conditions.index(self.condition)+1]

        # Если Дона и Шерифа нет в игре переходим на следующую стадию
        if self.condition in ['Don', 'EndDon', 'Sheriff', 'EndSheriff'] and self.don_appear == 0:
            return self.next_condition()

        return phrase

    def get_roles(self):
        """Получение ролей"""
        assert self.condition == Game.conditions[0], 'Incorrect condition'  # Получение ролей возможно только после регистрации
        assert roles.minimum <= len(
            self.players) <= roles.maximum, 'Incorrect count of players'  # Проверка количества игроков
        roles_list = roles.roles[str(len(self.players))]
        shuffle(roles_list)
        if len(self.players) >= roles.don_appear:
            self.don_appear = 1
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

    def kill(self):
        """Убийство игрока"""
        # Смена статуса жизни на 0
        for i in range(len(self.players)):
            if self.players[i].id == self.killed:
                self.players[i].alive = 0
                # Если убили Дона голосовалка перекидывается на мафию
                if str(self.players[i].role) == roles.don:
                    for j in range(len(self.players)):
                        if str(self.players[j].role) == roles.mafia:
                            self.players[j].role.vote = 1
                            break
                break

    def vote(self, player_id: int, vote_id: int):
        """Голосование за игрока player_id - за кого голосуют
        vote_id - кто голосует"""
        vote_name = vote_surname = ''
        for i in range(len(self.players)):
            if self.players[i].id == vote_id:
                vote_name = self.players[i].first_name
                vote_surname = self.players[i].last_name
                if self.players[i].vote == 1:
                    return f'{self.players[i].first_name} {self.players[i].last_name}, Вы уже голосовали!'  # Игрок голосует только 1 раз
                else:
                    self.players[i].vote = 1
                    self.count_vote += 1
                    break
        for i in range(len(self.players)):
            if self.players[i].id == player_id:
                self.players[i].votes_count += 1
                return f'{vote_name} {vote_surname} отдаёт голос за {self.players[i].first_name} {self.players[i].last_name}'

    def check_end_game(self):
        """Проверяет продолжится ли игра или нет"""
        black_count = red_count = 0
        for player in self.alive_players:
            if str(player.role) in [roles.mafia, roles.don]:
                black_count += 1
            else:
                red_count += 1
        if black_count >= red_count:
            self.winner = 'Победила мафия!'
            return True
        elif black_count == 0:
            self.winner = 'Победил город!'
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
            self.killed = player_id

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

    def roles(self):
        """Вывод списка игроков и их ролей"""
        msg = ''
        for player in self.players:
            msg += f'{player.first_name} {player.last_name} - {player.role}\n'
        return msg

    def alive_mates_names(self, player_id: int):
        """Возвращает имена всех напарников этой мафии"""
        assert self.get_role_by_id(player_id).color == 'Black', 'Напарники емть только у чёпных'
        alive_mates = [f'{player.first_name} {player.last_name}' for player in self.black_alive_players if
                       player.id != player_id]
        return f"Твои напарники:\n{'; '.join(alive_mates)}" if alive_mates else 'Ты единственная мафия за столом!'

    @property
    def alive_players(self):
        """Все живые игроки"""
        return [player for player in self.players if player.alive == 1]

    @property
    def black_players(self):
        """Все черные игроки"""
        # Используется для проверки шерифа
        return [player for player in self.players if player.role.color == 'Black']

    @property
    def black_alive_players(self):
        """Все живые чёрные игроки"""
        # Используется для пересылки сообщений между мафиями
        return [player for player in self.players if player.alive == 1 and player.role.color == 'Black']

    @property
    def don(self):
        """Дон игры"""
        for player in self.players:
            if player.role.role == roles.don:
                return player

    @property
    def sheriff(self):
        """Шериф игры"""
        for player in self.players:
            if player.role.role == roles.sheriff:
                return player
