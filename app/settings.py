import os


class DbSettings:
    DB_URL = os.environ.get('DB_URL')


class AppSettings:
    TOKEN = os.environ.get('TOKEN')
