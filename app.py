from crypt import methods
from pydoc import resolve
from sys import flags
from urllib import response
from cs50 import  SQL
from flask import Flask,redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required,error
import requests
import os
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


@app.route("/",methods=["POST","GET"])
@login_required
def index():
    if request.method == "POST":
        title=request.form.get("title")
        try:
            api_key = os.environ.get("API_KEY")
            url = f"https://imdb-api.com/en/API/SearchMovie/{api_key}/{title}"
            response = requests.get(url)
            data = response.json()
            
            return render_template("results.html",data = data["results"])
        except:
            return "None"
    data = db.execute("SELECT DISTINCT(titleid) FROM list WHERE id LIKE ?;",session["user_id"])
    movies = []
    for row in data:
        id = row["titleid"]
        api_key = os.environ.get("API_KEY")
        movie = requests.get(f"https://imdb-api.com/en/API/Title/{api_key}/{id}")
        moviedata = movie.json()
        title = moviedata["title"]
        image = moviedata["image"]
        year = moviedata["year"]
        dic = {"id":id,"title":title,"image":image,"year":year}
        movies.append(dic)
    return render_template("index.html",data=movies)


@app.route("/login",methods=["GET","POST"])
def login():

    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")


        if not (password and username):
        
            return error("Username or Password not provided","404")
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
            return error(code="402",message="user already exist")
        if password != confirm:
            return error(code = "402",message = " passwords doesnt match")
        
        hash = generate_password_hash(password)
        # Insert into Database
        db.execute("INSERT INTO users (username,hash) VALUES(?,?);",username,hash)
        return redirect("/login")
    return render_template("register.html")


@app.route("/add",methods=["POST"])
def add():
    title = request.form.get("id")
    user_id = session["user_id"]
    db.execute("INSERT INTO list (id ,titleid) VALUES(?,?);",user_id,title)
    return redirect("/")
