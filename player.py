class Player:
    """Класс, содержащий информацию об игроке"""
    def __init__(self, id: int, first_name: str, last_name: str):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.role = ''
        self.alive = 1
        self.vote = 0
        self.votes_count = 0

    def info(self):
        print(self.id, self.first_name, self.last_name, self.role, self.alive, self.vote, self.votes_count)
