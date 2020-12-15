from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

metadata = MetaData()

def get_session_maker(database_url):
    engine = create_engine(
        database_url
    )
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

