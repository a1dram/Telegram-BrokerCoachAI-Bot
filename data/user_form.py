from sqlalchemy import Column, String, Integer, Boolean

from data.database import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    dialog_have = Column(Boolean, default=False)
    dialog = Column(String, default="")
    client_personality = Column(String, default="An ordinary resident")
    client_trait = Column(String, default="no traits")
