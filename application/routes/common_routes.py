from flask import render_template

def register(app):

    @app.route("/")
    def welcome():
        return render_template("welcome.html")
