from flask import session, g
from database import create_app
from models import User
from blueprints import *

app = create_app()

app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(file)


@app.before_request
def my_before_request():
    user_id = session.get("user_id")
    if user_id:
        user = User.get_by(user_id=user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


@app.context_processor
def my_context_processor():
    return {"user": g.user}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
