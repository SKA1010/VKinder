import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object


metadata = MetaData()
Base = declarative_base()


def add_users(owner_id, user_id):
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        to_bd = users(profile_id=owner_id, worksheet_id=user_id)
        session.add(to_bd)
        session.commit()
    return "Запись добавлена"


def insert_users(owner_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        from_bd = session.query(users).filter(users.profile_id == owner_id).all()
        for item in from_bd:
            return item.profile_id

class users(Base):
    __tablename__ = 'users'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

if __name__ == '__main__':
    Base.metadata.drop_all()
    Base.metadata.create_all()