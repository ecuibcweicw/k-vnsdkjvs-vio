import sqlite3 as sq

class DataBase:
    def __init__(self, db_file):
        self.connection = sq.connect(db_file)
        self.cur = self.connection.cursor()

    def db_start(self):
        with self.connection:
            self.cur.execute('CREATE TABLE IF NOT EXISTS users('
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'user_id INTEGER NOT NULL,'
                             'count_play INTEGER NOT NULL DEFAULT 0,'
                             'win INTEGER NOT NULL DEFAULT 0,'
                             'lose INTEGER NOT NULL DEFAULT 0,'
                             'balance_win FLOAT NOT NULL DEFAULT 0,'
                             'balance_lose FLOAT NOT NULL DEFAULT 0,'
                             'refere_id INTEGER,'
                             'balance_ref INTEGER NOT NULL DEFAULT 0,'
                             'UNIQUE(user_id))')

    def db_stats(self):
        with self.connection:
            self.cur.execute('CREATE TABLE IF NOT EXISTS stats('
                             'count_play INTEGER NOT NULL DEFAULT 0,'
                             'win INTEGER NOT NULL DEFAULT 0,'
                             'lose INTEGER NOT NULL DEFAULT 0,'
                             'balance_win FLOAT NOT NULL DEFAULT 0,'
                             'balance_lose FLOAT NOT NULL DEFAULT 0)')

    def db_settings(self):
        with self.connection:
            self.cur.execute('CREATE TABLE IF NOT EXISTS settings('
                             'fake INTEGER NOT NULL DEFAULT 0,'
                             'KEF1 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF2 FLOAT NOT NULL DEFAULT 1.3,'
                             'KEF3 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF4 FLOAT NOT NULL DEFAULT 2.7,'
                             'KEF5 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF6 FLOAT NOT NULL DEFAULT 3,'
                             'KEF7 FLOAT NOT NULL DEFAULT 5,'
                             'KEF8 FLOAT NOT NULL DEFAULT 4,'
                             'KEF9 FLOAT NOT NULL DEFAULT 7,'
                             'KEF10 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF11 FLOAT NOT NULL DEFAULT 1.2,'
                             'KEF12 FLOAT NOT NULL DEFAULT 1.2,'
                             'KEF13 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF14 FLOAT NOT NULL DEFAULT 3,'
                             'KEF15 FLOAT NOT NULL DEFAULT 2.5,'
                             'KEF16 FLOAT NOT NULL DEFAULT 1.7,'
                             'KEF17 FLOAT NOT NULL DEFAULT 5,'
                             'KNB INTEGER NOT NULL DEFAULT 100)')

    def db_urls(self):
        with self.connection:
            self.cur.execute('CREATE TABLE IF NOT EXISTS urls('
                             'channals TEXT,'
                             'checks TEXT,'
                             'rules TEXT,'
                             'transfer TEXT,'
                             'command_game TEXT,'
                             'info_stavka TEXT,'
                             'news TEXT)')


    # Забираем статистику по проекту за день
    def all_stats_day(self):
        with self.connection:
            return self.cur.execute('SELECT count_play, win, lose, balance_win, balance_lose FROM stats').fetchone()

    #Забираем статистику по проекту
    def all_stats(self):
        with self.connection:
            return self.cur.execute('SELECT sum(count_play), sum(win), sum(lose), sum(balance_win), sum(balance_lose), count(user_id) FROM users').fetchall()[0]

    #Забираем статистику по пользователям
    def all_stats_users(self, user):
        with self.connection:
            return self.cur.execute('SELECT count_play, win, lose, balance_win, balance_lose, balance_ref FROM users WHERE user_id = ?', (user,)).fetchone()


    def add_users(self, user_id, refere_id=None):
        with self.connection:
            if refere_id != None:
                return self.cur.execute('INSERT INTO users (user_id, refere_id) VALUES (?, ?)', (user_id, refere_id))
            else:
                return self.cur.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))

    # Забираем сколько заработано с рефералов
    def refka_cheks_money(self, user_id):
        with self.connection:
            return self.cur.execute('SELECT balance_ref FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

    #Прибавка сколько юзер заработал с рефералов
    def add_balances_ref(self, user_id, amount):
        with self.connection:
            return self.cur.execute('UPDATE users SET balance_ref = balance_ref + ? WHERE user_id = ?', (amount, user_id))


    def count_ref(self, user_id):
        with self.connection:
            return self.cur.execute("SELECT COUNT(id) as 'Количество_рефералов' FROM users WHERE refere_id = ?",
                               (user_id,)).fetchone()[0]

    # Забираем реферала
    def select_referi(self, user_id):
        with self.connection:
            return self.cur.execute('SELECT refere_id FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

    #Проверка на юзера
    def user_exists(self, user_id):
        with self.connection:
            result = self.cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
            return bool(len(result))


    #Обновляем количество игр
    def add_count_pay(self, user_id, text, amount):
        with self.connection:
            if text == 'win':
                return self.cur.execute(f'UPDATE users SET count_play = count_play + 1, win = win + 1, balance_win = balance_win + {amount} WHERE user_id = {user_id}')
            if text == 'lose':
                return self.cur.execute(f'UPDATE users SET count_play = count_play + 1, lose = lose + 1, balance_lose = balance_lose + {amount} WHERE user_id = {user_id}')


    #Обновляем количество игр
    def add_count_pay_stats_day(self, text, amount):
        with self.connection:
            if text == 'win':
                return self.cur.execute(f'UPDATE stats SET count_play = count_play + 1, win = win + 1, balance_win = balance_win + {amount}')
            if text == 'lose':
                return self.cur.execute(f'UPDATE stats SET count_play = count_play + 1, lose = lose + 1, balance_lose = balance_lose + {amount}')


 #Обновляем количество игр
    def del_stats_day(self):
        with self.connection:
            return self.cur.execute(f'UPDATE stats SET count_play = 0, win = 0, lose = 0, balance_win = 0, balance_lose = 0')



    # Забираем значение вкл выкл фейк ставок
    def get_fake_values(self):
        with self.connection:
            return self.cur.execute('SELECT fake FROM settings').fetchone()[0]


    #Обновляем вкл выкл фейк ставок
    def update_fake(self, values):
        with self.connection:
            return self.cur.execute(f'UPDATE settings SET fake = ?', (values,))


    # Забираем все кэффициенты
    def get_all_KEF(self):
        with self.connection:
            res = self.cur.execute('SELECT * FROM settings').fetchone()
            return {'KEF1': res[1],'KEF2': res[2],'KEF3': res[3],'KEF4': res[4],'KEF5': res[5],'KEF6': res[6],'KEF7': res[7],
                    'KEF8': res[8],'KEF9': res[9],'KEF10': res[10],'KEF11': res[11],'KEF12': res[12],'KEF13': res[13],'KEF14': res[14],
                    'KEF15': res[15],'KEF16': res[16],'KEF17': res[17]}



    #Обновляем кеф
    def update_kef(self, column, values):
        with self.connection:
            return self.cur.execute(f'UPDATE settings SET {column} = ?', (values,))


    # Забираем кэффициент на игру
    def get_cur_KEF(self, column):
        with self.connection:
            return self.cur.execute(f'SELECT {column} FROM settings').fetchone()[0]


    # Забираем подкрут КНБ
    def get_KNB_procent(self):
        with self.connection:
            return self.cur.execute(f'SELECT KNB FROM settings').fetchone()[0]


    #Выгрузить всех юзеров
    def all_user(self):
        with self.connection:
            return self.cur.execute('SELECT user_id FROM users').fetchall()



    # Забираем ссылку
    def get_URL(self):
        with self.connection:
            result = self.cur.execute(f'SELECT * FROM urls').fetchone()
            return {'channals':result[0], 'checks':result[1], 'rules':result[2], 'transfer':result[3], 'command_game':result[4], 'info_stavka':result[5], 'news':result[6]}



    #Обновляем ссылку
    def update_url(self, column, values):
        with self.connection:
            return self.cur.execute(f'UPDATE urls SET {column} = ?', (values,))