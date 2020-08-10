mafia, don, civilian, sheriff = 'Мафия', 'Дон', 'Мирный житель', 'Коммисар'
minimum, maximum = 1, 7
don_appear = 6


class Role:
    def __init__(self, role: str, vote: int = None):
        assert role in (mafia, don, civilian, sheriff)
        self.role = role
        self.color = 'Black' if role in (mafia, don) else 'Red'
        self.vote = vote  # убивает ли эта мафия

    def __str__(self):
        return self.role


roles = {'1': [Role(mafia, 1)], '2': [Role(mafia, 1), Role(civilian)], '3': [Role(mafia, 1)]+[Role(civilian)]*2,
         '4': [Role(civilian)]*3+[Role(mafia, 1)], '5': [Role(civilian)]*4+[Role(mafia, 1)],
         '6': [Role(civilian)]*3+[Role(don, 1)]+[Role(mafia, 0)]+[Role(sheriff)],
         '7': [Role(civilian)]*4+[Role(don, 1)]+[Role(mafia, 0)]+[Role(sheriff)]}
