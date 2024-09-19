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
