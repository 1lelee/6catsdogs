from flask import Blueprint, render_template, g
from forms import FileForm

home = Blueprint("home", __name__, url_prefix="/")


@home.route("/")
@home.route("/home")
def welcome():
    user = g.user
    if not user:
        return render_template("index.html")

    return render_template("index.html", username=user.username, form=FileForm())
