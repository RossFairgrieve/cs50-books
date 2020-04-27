import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
# Could have used with engine.connect as connection:

def main():

    # Create BOOKS table
    db.execute("DROP TABLE books, users, reviews")
    db.commit()

if __name__ == "__main__":
    main()
