import os


class DbSettings:
    DB_URL = os.getenv('DATABASE_URL')
