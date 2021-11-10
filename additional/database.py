from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# data for sql engine 'postgresql://<username>:<password>@<ip-address/<hostname>/<database_name>'
SQLALCHEMY_DATABES_URL = 'postgresql://postgres:Xodavi321@localhost/fastapi'

engine = create_engine(SQLALCHEMY_DATABES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
