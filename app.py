
import datetime
from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from pymongo import MongoClient


def create_app():

    def replace_none(string):
        if string == None or string == "":
            string = "None"
        return string

    app = Flask(__name__)
    app.secret_key = "gg1234"  #baraie ramz dadan be session
    app.permanent_session_lifetime = timedelta(days=1)
    client = MongoClient("mongodb+srv://username:password@microblog-1.tk0zu8o.mongodb.net/test")
    app.db = client.microblog


    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST" and request.form["id"] == "":
            entry_title = session["username"]
            entry_content = replace_none(request.form.get("content"))
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            show_date = datetime.datetime.strptime(formatted_date, "%Y-%m-%d").strftime("%b %d")
            entry = {
                "entry_title" : entry_title,
                "entry_content" : entry_content,
                "formatted_date" : formatted_date,
                "show_date" : show_date
            }
            app.db.entries.insert_many([entry])
        
        elif request.method == "POST" and request.form["id"] != "":
            for i in app.db.entries.find():
                if str(i) == request.form["id"]:
                    app.db.entries.delete_many(i)
        
        if "username" in session:
            username = session["username"]
            log = True
        else:
            username = "Login"
            log = False
        
        entries = [i for i in app.db.entries.find()]
        return render_template("home.html", entries=entries, username=username, log=log)
    
    @app.route("/signup", methods=["POST", "GET"])
    def signup():
        if request.method == "POST":
            session.permanent = True
            username = request.form["username"]
            if username == "":
                flash("Please enter name", "info")
                return redirect(url_for("signup"))
            
            if app.db.users.find_one({"username":username}):
                flash("The username is already being used!", "info")
                return redirect(url_for("signup"))

            password = request.form["password"]
            password_2 = request.form["password_2"]
            if len(password) < 8 or password != password_2:
                flash("Please enter password", "info")
                return redirect(url_for("signup"))
            
            user = {"username":username, "password":password}
            app.db.users.insert_many([user])
            session["username"] = username
            session["password"] = password
            flash("Sign up Succesful!", "info")
            return redirect(url_for("home"))
        else:
            if "username" in session:
                flash("You Logged In!", "info")
                return redirect(url_for("home"))
            else:
                return  render_template("signup.html")

    @app.route("/login", methods=["POST", "GET"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if app.db.users.find_one({"username":username}):
                user = app.db.users.find_one({"username":username})
                if user["password"] == password:
                    session.permanent = True
                    session["username"] = username
                    session["password"] = password
                    flash("Login Succesful!", "info")
                    return redirect(url_for("home"))
                else:
                    flash("Password is not correct!", "info")
                    return render_template("login.html")
            flash("Username not found!", "info")
            return render_template("login.html")
        else:
            if "username" in session:
                flash("You Logged In!", "info")
                return redirect(url_for("home"))
            else:
                return  render_template("login.html")

    @app.route("/logout", methods=["POST", "GET"])
    def logout():
        if "username" in session:
            usr = session["username"]
            flash(f"You have been logged out {usr}!", "info")
        session.pop("username", None)
        session.pop("password", None)
        return redirect(url_for("home"))

    return app
