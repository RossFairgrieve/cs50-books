import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# Could have used with engine.connect as connection:

def main():

    # Import csv file of books
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)
    for isbn, title, author, year in reader:
        try:
            year = int(year)
        except:
            year = 0
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn":isbn, "title":title, "author":author, "year":year})
        # print(f"Added {isbn} - {title} by {author} ({year})")
    db.commit()

if __name__ == "__main__":
    main()
