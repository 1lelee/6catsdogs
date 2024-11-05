from flask import (
    Blueprint,
    render_template,
    jsonify,
    redirect,
    request,
    url_for,
    session,
    flash,
)
from database import mail
from flask_mail import Message
import string
import random
from models import User
from forms import RegisterForm, LoginForm, FileForm
from db import *

# /auth
auth = Blueprint("auth", __name__, url_prefix="/auth")


# 登录
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "GET":
        return render_template("login.html", form=form)
    else:
        # form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            # 如果有多个记录匹配查询条件，它只返回第一条记录
            # user = User.query.filter_by(username=username).first()
            user = User.get_by(username=username)
            if not user:
                flash("用户未注册！")
                print("用户在数据库中不存在！")
                return redirect(url_for("auth.login"))

            # 输入密码哈希值与数据库中内容对照
            import Encryption_and_decryption as ed

            print(password)
            print(user.hash_password)
            if ed.check_password_get(password, user.hash_password):
                # cookie：
                # cookie中不适合存储太多的数据，只适合存储少量的数据
                # cookie一般用来存放登录授权的东西
                # flask中的session，是经过加密后存储在cookie中的
                session["user_id"] = user.user_id
                session["is_vip"] = user.is_vip
                print(session)
                print(session["user_id"])
                # print(session['username'])
                # return "成功登录"
                 
                return redirect(url_for("home.welcome"))

            else:
                flash("密码错误！")
                print("密码错误！")
        else:
            print(form.errors)
            flash(form.errors)

        return render_template("login.html", form=form)


# 注册
@auth.route("/register", methods=["GET", "POST"])
def register():
    # 验证用户提交的邮箱和验证码是否对应且正确
    # 表单验证：flask-wtf: wtforms
    form = RegisterForm(request.form)
    if request.method == "GET":
        return render_template("register.html", form=form)
    else:
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            print("form.password.data", password)
            # 密码不能明文存储，在数据库表中使用generate_password_hash(password)生成hash值存储
            import Encryption_and_decryption as ed

            hash_password = ed.get_hash_from_str(password)
            print("hash_password", hash_password)
            user_salt = ed.user_key_generate(hash_password)[2]
            # user = User(
            #     email=email,
            #     username=username,
            #     hash_password=hash_password,
            #     user_salt=user_salt,
            #     is_vip = False
            # )
            # # session['username'] = username
            # db.session.add(user)
            # db.session.commit()
            is_vip = False
            add_user(username, hash_password, user_salt, email, is_vip)

            flash("注册成功！")
            return redirect(url_for("auth.login"))
        else:
            print(form.errors)
            flash(form.errors)

        return render_template("register.html", form=form)


# 退出登录
@auth.route("/logout")
def logout():
    # 获取当前路径
    current_path = request.referrer
    print(current_path)
    session.clear()
    if current_path and "/shared_file/" in current_path:
        return redirect(current_path)
    else:
        return redirect("/")


# 获取邮箱验证码
# auth.route：如果没有指定methods参数，默认就是GET请求
@auth.route("/captcha/email")
def get_email_captcha():
    # /captcha/email/<email>
    # /captcha/email?email=xxx@qq.com
    email = request.args.get("email")
    # 4/6：随机数组、字母、数组和字母的组合
    source = string.digits * 6
    captcha = random.sample(source, 6)
    captcha = "".join(captcha)
    # I/O：Input/Output
    message = Message(
        subject="中传放心传-注册验证码",
        recipients=[email],
        body=f"您的验证码是:{captcha}",
    )
    mail.send(message)
    # memcached/redis
    # 用数据库表的方式存储
    add_email_captcha(email, captcha)
    # RESTful API
    # {code: 200/400/500, message: "", data: {}}
    return jsonify({"code": 200, "message": "", "data": None})
