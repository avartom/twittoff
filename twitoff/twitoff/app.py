from re import DEBUG
from flask import Flask, render_template, request
from .predict import predict_user
from .models import DB, User, Tweet
from .twitter import update_all_users, add_or_update_user

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    DB.init_app(app)
    
    @app.route('/')
    def root():
        return render_template('base.html', title= "Home")

    @app.route('/update')
    def update():
        usernames = get_all_usernames()
        for username in usernames:
            add_or_update_user(username)
        return "All users have been updated"
    
    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template("base.html", title="Reset Database")

    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = "User {} Successfully added!".format(name)
            tweets = User.query.filtee(User.username == name).one().tweets
        except Exception as e:
            message = "Error adding {}: {}".format(name, e)
            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted([request.values['user0'], request.value["user1"]])
        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            prediction = predict_user(user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".forma(request.values["tweet_text"], user1 if prediction else user0, user0 if prediction else user1)
        
        return render_template('prediction.html', title="Prediction", message=message)

    return app