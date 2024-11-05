import random

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = ''.join(random.choice("il1I|") for i in range(20))+'C0nGr@ts'+''.join(random.choice("il1I|") for i in range(20))+'u_can_$et_AcCEss_T0||v~Ip_UsEr_s_HoMe||:)'+''.join(random.choice("il1I|") for i in range(20))

# 数据库参数设置 运行前需修改 
HOSTNAME = '127.0.0.1'
PORT='3306'
DATABASE = '6catdogs' # Cainiao E Station database的缩写
USERNAME = 'root' # 用户名
PASSWORD = '' # 数据库密码
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = DB_URI

# 验证码发送邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "muttonbuns@qq.com"
MAIL_PASSWORD = "zxcfshkprmnycega"
MAIL_DEFAULT_SENDER = "muttonbuns@qq.com"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
storage_path = os.path.join(BASE_DIR, 'uploads/')

# 如果 uploads 文件夹不存在，则自动创建
os.makedirs(storage_path, exist_ok=True)

