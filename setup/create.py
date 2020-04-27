import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# Could have used with engine.connect as connection:

def main():

    # Create BOOKS table
    db.execute("""CREATE TABLE books (
               isbn VARCHAR PRIMARY KEY,
               title VARCHAR NOT NULL,
               author VARCHAR NOT NULL,
               year INTEGER NOT NULL);""")

    # Create REVIEWS table
    db.execute("""CREATE TABLE reviews (
               id SERIAL PRIMARY KEY,
               username VARCHAR NOT NULL,
               isbn VARCHAR NOT NULL,
               rating INTEGER NOT NULL,
               revtext TEXT NOT NULL);""")

    # Create USERS table
    db.execute("""CREATE TABLE users (
               username VARCHAR PRIMARY KEY,
               password VARCHAR NOT NULL,
               fname VARCHAR NOT NULL,
               surname VARCHAR NOT NULL);""")

    db.commit()

if __name__ == "__main__":
    main()
