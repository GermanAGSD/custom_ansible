from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

from pydantic.types import conint


class LdapUsers(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode: True

class CreateHostGroup(BaseModel):
    grouptype: str = Field(..., example="Linux")
    description: str = Field(..., example="For Server")

    class Config:
        orm_mode = True

class DeleteHostGroup(BaseModel):
    id: int
    # grouptype: str = Field(..., example="Linux")
    # description: str = Field(..., example="For Server")

    class Config:
        orm_mode = True


# Pydantic-схема для валидации входных данных
class HostCreateSchema(BaseModel):
    ipadress: str = Field(..., example="192.168.1.1")
    port: str = Field(..., example="22")
    username: str = Field(..., example="user")
    password: str = Field(..., min_length=8, example="password123")
    grouptype_id: int = Field(..., example=1)

    class Config:
        orm_mode = True

# Pydantic-схема для валидации входных данных
class HostFileSchema(BaseModel):
    ipadress: str = Field(..., example="192.168.1.1")
    # port: str = Field(..., example="22")
    # username: str = Field(..., example="user")
    # password: str = Field(..., min_length=8, example="password123")
    # grouptype_id: int = Field(..., example=1)

    class Config:
        orm_mode = True

# Создаем Pydantic-схему для возврата данных
class HostResponse(BaseModel):
    id: int
    ipadress: str
    port: str
    username: str
    # grouptype_id: int
    # password: str

    class Config:
        orm_mode = True

# Модель данных для запроса POST
class HostCreate(BaseModel):
    ipadress: str
    port: str
    username: str
    password: str
    grouptype_id: int
    
    class Config:
        orm_mode = True
# Создаем Pydantic-схему для возврата данных
class HostType(BaseModel):
    id: int
    grouptype: str
    description: str


    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    groups: Optional[str] = []

class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
