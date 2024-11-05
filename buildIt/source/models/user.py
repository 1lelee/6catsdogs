from sqlalchemy.types import BINARY
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, '..', 'instance')
db_path = os.path.join(db_dir, '6dac.db')

class User:
    def __init__(self, user_id, username, hash_password=None, user_salt=None, email=None, join_time=None, is_vip=False):
        self.user_id = user_id
        self.username = username
        self.hash_password = hash_password
        self.user_salt = user_salt
        self.email = email
        self.join_time = join_time
        self.is_vip = is_vip

    # 用于在数据库中查询用户
    @classmethod
    def get_by(cls, **kwargs):
        conditions = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        query = f"SELECT * FROM user WHERE {conditions}"
        values = tuple(kwargs.values())

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()
        conn.close()

        if result:
            return cls(*result)
        return None

# 邮件验证码
class EmailCaptchaModel:
    def __init__(self, id, email, captcha):
        self.id = id
        self.email = email
        self.captcha = captcha

    @classmethod
    def get_by(cls, **kwargs):
        conditions = " AND ".join(f"{key} = ?" for key in kwargs.keys())
        query = f"SELECT * FROM email_captcha WHERE {conditions}"
        values = tuple(kwargs.values())

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        result = cursor.fetchone()
        conn.close()

        if result:
            return cls(*result)
        return None
