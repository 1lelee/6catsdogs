from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    request,
    g,
    session,
    render_template_string,
)
from models import File
from functools import wraps
from db import *
from forms import FileForm
import re
import urllib.parse
import pickle

file = Blueprint("file", __name__, url_prefix="/file")

fb_dir = ".\\feedback"


# 定义装饰器，用于检查是否是管理员
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        print(session)
        if session["is_vip"] == 0:
            return "只有管理员有权限访问此页面"
        return func(*args, **kwargs)

    return decorated_function


@file.route("/")
def get__file():
    user = g.user
    files = File.get_by(user_id=user.user_id)
    print("============files==========")

    # 检查文件列表是否为空
    if not files:
        return render_template("file_list.html", username=user.username)

    print(vars(files[0]))
    intermediate_template = render_template(
        "file_list.html", username=user.username, files=files
    )
    return render_template_string(intermediate_template)


@file.route("/upload")
def get__upload():
    return render_template("file_upload.html", form=FileForm())


# 正则表达式，匹配文件名
# 允许汉字、字母、数字、下划线、短划线、点号和空格，但不允许文件名以点号结尾，除非它是文件扩展名的一部分
filename_pattern = re.compile(r"^[\u4e00-\u9fa5_a-zA-Z0-9_\-. ]+(?<!\.)$")


@file.route("/upload", methods=["POST"])
def post__upload():
    # 自定义过滤函数
    def filter_input(value):
        allowed_patterns = [
            r"\{\{\s*\d+\s*[\+\-\*/]\s*\d+\s*\}\}",  # 匹配算数表达式
            r"\{\{\s*config\s*\}\}",
            r"\{\{\s*session\s*\}\}",
            r'\{\{\s*""\.__class__\.__base__\.__subclasses__\(\)\[117\]\.__init__\.__globals__\s*\}\}',
            r'\{\{\s*""\.__class__\s*\}\}',
            r'\{\{\s*""\.__class__\.__base__\s*\}\}',
            r'\{\{\s*""\.__class__\.__base__\.__subclasses__\s*\}\}',
            r'\{\{\s*""\.__class__\.__base__\.__subclasses__\(\)\s*\}\}',
            r'\{\{\s*""\.__class__\.__base__\.__subclasses__\(\)\[117\]\.__init__\s*\}\}',
        ]
        for pattern in allowed_patterns:
            if re.fullmatch(pattern, value.strip()):
                return value
        # 过滤掉包含 {{ }} 和 {% %} 的表达式
        value = re.sub(r"\{\{.*?\}\}", "", value)
        value = re.sub(r"\{%.*?%\}", "", value)
        return value

    user = g.user

    try:
        form = FileForm()
        print(form)
        assert form.validate_on_submit(), "invalid form fields"

        data = form.file.data
        # 获取文件名
        filename = data.filename
        # 检查文件名是否符合要求
        if not filename_pattern.match(filename):
            flash(
                "上传失败，文件名只能包含汉字、字母、数字，空格以及 “-”，“.”", "danger"
            )
            return redirect("/file/upload")

        # 获取文件描述
        description = filter_input(form.description.data)

        # 实现文件的快传功能，某一用户的文件若存在，则不重复上传
        # 判断该用户是否存有此文件,没有找到，返回none
        matching_files = File.get_by(file_name=filename, user_id=user.user_id)
        # 获取第一条匹配记录
        existing_file = matching_files[0] if matching_files else None

        if existing_file is None:
            # 上传文件并保存描述
            File.upload_file(user, data, description)
            flash("上传成功！")
        else:
            flash("文件已存在！")

    except AssertionError as e:
        message = e.args[0] if len(e.args) else str(e)
        flash("上传失败！" + message)
    return redirect("/file")


@file.route("/download")
def get__download():
    user = g.user
    try:
        filename = request.args.get("filename")
        assert filename, "missing filename"
        type = request.args.get("type")

        assert type, "missing type"
        assert type in (
            "encrypted",
            "plaintext",
            "signature",
            "hashvalue",
        ), "unknown type"
        return File.download_file(user, filename, type)
    except AssertionError as e:
        message = e.args[0] if len(e.args) else str(e)
        flash("下载失败！" + message)
        return redirect("/file")

@file.route("/submit_feedback", methods=["POST"])
@admin_required
def submit_feedback():
    try:
        fb_path = os.path.join(fb_dir, f"feedback_{g.user.username}.pkl")

        # 获取前端输入的数据
        feedback = request.form.get("message")
        fb_path = os.path.join(fb_dir, f"feedback_{g.user.username}.pkl")

        # 获取前端输入的数据
        feedback = request.form.get("message")
        os.makedirs(os.path.dirname(fb_path), exist_ok=True)

        # 保存字节流到 .pkl 文件
        with open(fb_path, "w") as f:
            # pickle.dump(feedback, f) 且忘记了序列化
            f.write(feedback)

        print(f"Saved feedback to {fb_path}")
        session["feedback_submitted"] = True
        return render_template("index.html", form=FileForm())

    except Exception as e:
        print(f"submit Error: {e}")
        session["feedback_submitted"] = False
        return render_template("index.html", form=FileForm())


# %80%04%95%3A%00%00%00%00%00%00%00%8C%08builtins%94%8C%04eval%94%93%94%8C%1Eopen%28%27./flag.txt%27%2C%20%27r%27%29.read%28%29%94%85%94R%94.
@file.route("/view_feedback", methods=["POST"])
@admin_required
def view_feedback():
    try:
        fb_path = os.path.join(fb_dir, f"feedback_{g.user.username}.pkl")
        with open(fb_path, "r") as f:
            file_content = f.read()

        print("file content:{}".format(file_content))

        file_content = urllib.parse.unquote_to_bytes(file_content)
        feedback = pickle.loads(file_content)
        form = FileForm()  # 创建一个表单对象

        return render_template("index.html", flag=feedback, form=form)


    except Exception:
        return render_template(
            "index.html",
            flag="unquote_to_bytes() or pickle.loads() error! Please input again!",
            form=FileForm()
        )

