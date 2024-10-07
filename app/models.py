from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    history = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
    # Внешний ключ, ссылающийся на id таблицы Type
    grouptype_id = Column(Integer, ForeignKey('group.id'), nullable=True)
    
    # Отношение между Hosts и Type
    grouptype = relationship("Group", back_populates="users")
class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    users = relationship("Users", back_populates="grouptype")

class Hosts(Base):
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ipadress = Column(String, nullable=False)
    port = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Внешний ключ, ссылающийся на id таблицы Type
    grouptype_id = Column(Integer, ForeignKey('type.id'), nullable=True)
    
    # Отношение между Hosts и Type
    grouptype = relationship("Type", back_populates="hosts")

class Type(Base):
    __tablename__ = "type"
    id = Column(Integer, primary_key=True, autoincrement=True)
    grouptype = Column(String, nullable=False)
    description = Column(String, nullable=False)
    # Отношение к таблице Hosts
    hosts = relationship("Hosts", back_populates="grouptype")
