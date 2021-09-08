from typing import List, Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
    content:str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    commentator_username: str
    post_id: int

    class Config:
        orm_mode = True


class BlogBase(BaseModel):
    title: str
    content:str


class BlogCreate(BlogBase):
    pass


class Blog(BlogBase):
    id: int
    author_username: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    email: str
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    blogs: List[Blog] = []
    comments: List[Comment] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
