import sqlite3
import random
import sqlite3
import os

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "instance")
db_path = os.path.join(db_dir, "6dac.db")


# 判断表是否存在
def table_exists(table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False


# 检查是否已经执行过初次建表操作了
def check_tables_exist():
    tables = ["user", "email_captcha", "file"]

    for table in tables:
        if not table_exists(table):
            return False

    return True


def create_instance_directory():
    # 如果 instance 目录不存在，则创建它
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)


create_instance_directory()


def create_email_captcha():
    # Only run this to reset the database file!
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # cursor.execute('DROP TABLE IF EXISTS email_captcha')

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS email_captcha (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email VARCHAR(100) NOT NULL,
        captcha VARCHAR(10) NOT NULL
    )
    """
    )

    # cursor.execute('''
    # INSERT INTO todo(id, content, completed, date_created)
    # SELECT id, content, completed, date_created FROM todo
    # ''')

    conn.commit()
    conn.close()


def create_user():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # cursor.execute('DROP TABLE IF EXISTS user')

    # Create the user table
    cursor.execute(
        """
    CREATE TABLE user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(128) NOT NULL,
        hash_password BLOB DEFAULT NULL,
        user_salt BLOB DEFAULT NULL,
        email VARCHAR(100) NOT NULL,
        join_time DATETIME DEFAULT NULL,
        is_vip TINYINT DEFAULT NULL,
        UNIQUE (username)
        );
    """
    )

    # User data to be inserted
    users_data = [
        (
            "1",
            "LlYySs",
            b"$2b$12$22H6bZ0IOUD3TI0xl0GjyeGS/.QkjjhdEiFdHVyMHmmQqpWt5L6O.",
            b"zS\x03]\xa9Q\xcfg\x02\xean\xe2\xc5a\xf5\xfb\n\x83\xe6_\xac\x8e\xcf\xa8\xf9 \xd0;\xeb?\x93a\xea0\xaaA\x11Z;n\xd8cS\xa9I2s.\xec\x03]\xb8\xa0\x1f\x89\xe9\xc5\xa01\x9c\xc0\xfb\xad\xee\x92%\xd8/\xd8m\xec\xfe<m\n&\x85\xfb\xbb/\x0fo\x9d\x02\x9b\xd5H\xab)\xbf\x01{\xcaV\xc4\xc0\x81\x91\xb1X\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "1792791515@qq.com",
            "2024-07-12 00:29:52",
            "1",
        ),
        (
            "2",
            "test",
            b"$2b$12$hNJOn9qqJDq.AZXSbBtE2eLInxdoM3RXEPKbeFQN7UaqY1SWyZOAO",
            b"\xd8\x0b\x18*^\xf0f\xc1\x89v\x9f\xef\x17\x85\xa5\xa5\xe8dC\x17(\xef3[2\x14\xe6-\xc4P\x8d.\xcf\x81;\xbd\xd4xq\x0e\xc6\x08\x9b}\xc9+%N\x9dwqR\x1a\x0f\xcc\xa2\x18\xf2\x9d\xf0\xd6\xa3QAQ\x92\xe2./O\xe2s\xc2\x14]\x95S\xce\xdd\xeb\x82\x81xQ\xaf+\x0fB\xe4\xaa;~\xa9\xa6\xf4;\xed\xa4\xc4\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            "2874730541@qq.com",
            "2024-07-13 15:41:03",
            "0",
        ),
    ]

    # Check if username already exists in the database
    for user in users_data:
        cursor.execute("SELECT username FROM user WHERE username = ?", (user[1],))
        if cursor.fetchone():
            print(f"Username {user[1]} already exists. Skipping insertion.")
            continue
        cursor.execute(
            """
            INSERT INTO user (user_id,username,hash_password,user_salt,email,join_time, is_vip) VALUES (?, ?, ?, ?,?,?,?)
        """,
            user,
        )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# 注册时调用
def add_user(username_, hash_password_, user_salt_, email_, is_vip_):
    print(type(username_))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    from datetime import datetime

    join_time = datetime.now()

    # Insert the user data into the table
    users_data = (username_, hash_password_, user_salt_, email_, join_time, is_vip_)
    print(users_data)
    cursor.execute(
        "INSERT INTO user (username,hash_password,user_salt,email,join_time,is_vip) VALUES (?, ?, ?,?,?,?)",
        users_data,
    )

    conn.commit()
    conn.close()


def add_email_captcha(email_, captcha_):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    email_captcha_data = (email_, captcha_)
    print(email_captcha_data)

    cursor.execute(
        "INSERT INTO email_captcha (email, captcha) VALUES (?, ?)", email_captcha_data
    )

    conn.commit()
    conn.close()


# 创建file表
def create_file():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # cursor.execute('DROP TABLE IF EXISTS file')
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS file (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name VARCHAR(256),
        description VARCHAR(255),
        file_signature BLOB,  -- 使用 BLOB 存储二进制数据
        static_hash BLOB,      -- 使用 BLOB 存储二进制数据
        public_key BLOB,       -- 使用 BLOB 存储二进制数据
        FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
    )
    """
    )

    # cursor.execute('''
    # INSERT INTO todo(id, content, completed, date_created)
    # SELECT id, content, completed, date_created FROM todo
    # ''')

    conn.commit()
    conn.close()


# 上传文件时调用
def add_file(
    user_id_, file_name_, file_signature_, static_hash_, public_key_, description_
):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    file_data = (
        user_id_,
        file_name_,
        file_signature_,
        static_hash_,
        public_key_,
        description_,
    )
    print(file_data)

    cursor.execute(
        "INSERT INTO file (user_id, file_name, file_signature, static_hash, public_key, description) VALUES (?, ?, ?, ?, ?, ?)",
        file_data,
    )

    conn.commit()
    conn.close()
