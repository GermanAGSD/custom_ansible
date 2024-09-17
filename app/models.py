from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class Hosts(Base):
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, nullable=False)
    ipadress = Column(String, nullable=False)
    port = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Внешний ключ, ссылающийся на id таблицы Type
    grouptype_id = Column(Integer, ForeignKey('type.id'), nullable=False)
    
    # Отношение между Hosts и Type
    grouptype = relationship("Type", back_populates="hosts")

class Type(Base):
    __tablename__ = "type"
    
    id = Column(Integer, primary_key=True, nullable=False)
    grouptype = Column(String, nullable=False)
    
    # Отношение к таблице Hosts
    hosts = relationship("Hosts", back_populates="grouptype")
# class Device(Base):
#     __tablename__ = "devices"

#     id = Column(Integer, primary_key=True, nullable=False)
#     parrametr = Column(String, nullable=False)
#     info = Column(String, nullable=False)
#     published = Column(Boolean, server_default='TRUE', nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# class Post(Base):
#     __tablename__ = "posts"

#     id = Column(Integer, primary_key=True, nullable=False)
#     title = Column(String, nullable=False)
#     content = Column(String, nullable=False)
#     published = Column(Boolean, server_default='TRUE', nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True),
#                         nullable=False, server_default=text('now()'))
#     owner_id = Column(Integer, ForeignKey(
#         "users.id", ondelete="CASCADE"), nullable=False)

#     owner = relationship("User")


# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True),
#                         nullable=False, server_default=text('now()'))


# class Vote(Base):
#     __tablename__ = "votes"
#     user_id = Column(Integer, ForeignKey(
#         "users.id", ondelete="CASCADE"), primary_key=True)
#     post_id = Column(Integer, ForeignKey(
#         "posts.id", ondelete="CASCADE"), primary_key=True)
