mafia, don, civilian, sheriff = 'Мафия', 'Дон', 'Мирный житель', 'Шериф'
minimum, maximum = 2, 7
roles = {'2': [don, civilian], '3': [don, civilian, civilian], '4': [civilian]*3+[don], '5': [civilian]*4+[don],
         '6': [civilian]*3+[don]+[mafia]+[sheriff],
         '7': [civilian]*4+[don]+[mafia]+[sheriff]}
