from flask import Flask
from flask_wtf.csrf import CSRFProtect
import config
from flask_mail import Mail
from db import *

mail = Mail()

def create_app():
    
    app = Flask(__name__)
    # 开启CSRF保护
    CSRFProtect(app)

    app.config.from_object(config)
    mail.init_app(app)

    with app.app_context():
        # 只有在用户没建过表时才执行初始化表操作
        if not check_tables_exist():
            create_email_captcha()
            create_user()
            create_file()

    return app
