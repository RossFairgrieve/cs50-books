import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# session['username'] = None

@app.route("/")
def index():
    if session.get("username") == None:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("search"))
    # else:
    # return render_template("search.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html", show_logout=1)
    else:
        search_type = request.form.get("search_by")
        search_term = request.form.get("search_term").lower()
        if request.form.get("partial") == "partial":
            search_term = f"%{search_term}%"
        results = db.execute(f"SELECT * FROM books WHERE lower({search_type}) LIKE (:search_term);",
                             {"search_term": search_term}).fetchall()
        return render_template("search-results.html", results=results, num_results=len(results), show_logout=1)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Check for existing users with that username
        username = request.form.get("username")
        email = request.form.get("email")
        results = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if results != None:
            return render_template("register.html", message="Username already taken")
        results = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
        if results != None:
            return render_template("register.html", message="An account with that email address already exists")
        else:
            password = request.form.get("password")
            db.execute("""INSERT INTO users (username, password, email)
                        VALUES (:username, :password, :email)""",
                        {"username": username, "password": password, "email": email})
            db.commit()
            return render_template("registered.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check for existing user with that Username
        username = request.form.get("username")
        results = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if results == None:
            return render_template("login.html", message="Username does not exist.")
        else:
            password = request.form.get("password")
            if password == results.password:
                session["username"] = username
                return render_template("login-success.html", username=username, show_logout=1)
            else:
                return render_template("login.html", message="Password incorrect.")
    else:
        return render_template("login.html")

@app.route("/books/<isbn>", methods=["GET", "POST"])
def book(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn;", {"isbn": isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn;", {"isbn": isbn}).fetchall()
    if request.method == "GET":
        # List details of a single book
        return render_template("book.html", book=book, reviews=reviews, errormessage="", successmessage="", show_logout=1)
    else:
        # Get details from review form and attempt to post review
        username = session.get("username")
        isbn = request.form.get("isbn")
        rating = request.form.get("rating")
        revtext = request.form.get("revtext")
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn;", {"isbn": isbn}).fetchone()
        # Check to see if the reviewer has already posted a review of this book
        old_reviews = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn",
                             {"username": username, "isbn": isbn}).fetchone()
        # If user has already reviewed book, return to book page with alert
        if old_reviews != None:
            return render_template("book.html", book=book, reviews=reviews, errormessage="You have already reviewed this book", successmessage="", show_logout=1)
        # If user hasn't already reviewed book, write review to database
        else:
            db.execute("""INSERT INTO reviews (username, isbn, rating, revtext)
                       VALUES (:username, :isbn, :rating, :revtext)""",
                       {"username": username, "isbn": isbn, "rating": rating, "revtext": revtext})
            db.commit()
            return render_template("book.html", book=book, reviews=reviews, errormessage="", successmessage="Your review has been posted", show_logout=1)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
