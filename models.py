from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME

if DATABASE_USER is None:
    db_string = f'sqlite:///db1.db'
    print("No database credentials found, using sqlite")
else:
    db_string = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}/{DATABASE_NAME}'

db = create_engine(db_string)
base = declarative_base()


class BannedUsers(base):
    __tablename__ = 'black_list'

    id = Column("banned_user_id", Integer, primary_key=True)
    telegram_id = Column("telegram_id", Integer, unique=True)


Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)
