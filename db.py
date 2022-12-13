import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def request_to_database(self, request, *args):
        with self.connection:
            return self.cursor.execute(request, *args)

    def add_user(self, user_id, username):
        self.request_to_database("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username,))

    def user_exists(self, user_id):
        self.request_to_database(f"SELECT user_id FROM users WHERE user_id=?", (user_id,))
        return bool(len(self.cursor.fetchall()))

    def get_all_users(self):
        with self.connection:
            res = self.cursor.execute("SELECT user_id FROM users").fetchall()
            return [int(i[0]) for i in res]

    def add_group(self, group_href):
        self.request_to_database("INSERT INTO groups (href) VALUES (?)", (group_href,))

    def group_exists(self, group_href):
        self.request_to_database(f"SELECT href FROM groups WHERE href=?", (group_href,))
        return bool(len(self.cursor.fetchall()))

    def get_all_groups(self):
        with self.connection:
            res = self.cursor.execute("SELECT href FROM groups").fetchall()
            return [i[0] for i in res]


db = Database("dbase")
