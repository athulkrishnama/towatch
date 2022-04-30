from crypt import methods
from sys import flags
from cs50 import  SQL
from flask import Flask,redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required,error

# configure application

app = Flask(__name__)

# Ensure template auto reload

app.config["TEMPLATE_AUTO_RELOAD"] = True

# configure session

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Databse

db = SQL("sqlite:///user.db")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def login():

    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")


        if not (password and username):
        
            return error("404","Username or Password not provided")
        data = db.execute("SELECT * FROM users WHERE username LIKE ?;",username)
        if len(data) != 1 or not check_password_hash(data[0]["hash"],password):
            return error("invalid username or password","400")
        session["user_id"] = data[0]["id"]

        return redirect("/")


    return render_template("login.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not (password and username and confirm):
            return error("some data is missing","400")
        data = db.execute("SELECT username FROM users WHERE username LIKE ?; ",username)
        if len(data) != 0:
            return error("",code="user already exist")
        if password != confirm:
            return error("",code = " passwords doesnt match")
        
        hash = generate_password_hash(password)
        # Insert into Database
        db.execute("INSERT INTO users (username,hash) VALUES(?,?);",username,hash)
        return redirect("/login")
    return render_template("register.html")

