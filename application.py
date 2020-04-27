import os

from flask import Flask, session, render_template, request
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

logged_in = 0

@app.route("/")
def index():
    if logged_in == 1:
        return render_template("search.html")
    elif logged_in == 0:
        return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    search_type = request.form.get("search_by")
    search_term = request.form.get("search_term").lower()
    if request.form.get("partial") == "partial":
        search_term = f"%{search_term}%"
    results = db.execute(f"SELECT * FROM books WHERE lower({search_type}) LIKE (:search_term);",
                         {"search_term": search_term}).fetchall()
    return render_template("search_results.html", results=results, num_results=len(results))

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    global logged_in
    logged_in = 1
    return render_template("login-success.html", username=username)

@app.route("/books/<isbn>")
def book(isbn):
    # List details of a single book
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn;", {"isbn": isbn}).fetchone()
    return render_template("book.html", book=book)
