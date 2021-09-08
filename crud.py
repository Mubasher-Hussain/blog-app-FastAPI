import hashlib

from database import SessionLocal
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

import models, schemas


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="blogs/api/login/")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Security related methods
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Decodes jwt token to get current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# CRUD Operations
async def create_blog(
    db: Session, blog: 
    schemas.BlogCreate, 
    current_user: models.User = Depends(get_current_user)
):
    db_blog = models.Blog(**blog.dict(), author_username=current_user.username)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return {"Message": "Success"}


async def create_comment(
    db: Session, 
    comment: schemas.CommentCreate, 
    post_id: str, 
    current_user: models.User = Depends(get_current_user)
):
    db_comment = models.Comment(**comment.dict(), commentator_username=current_user.username, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return {"Message": "Success"}


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"Message" : "Success"}


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_blogs(db: Session, author: str = None):
    if author:
        return db.query(models.Blog).filter(models.Blog.author_username == author).all()
    return db.query(models.Blog).all()


def get_blog_details(db: Session, post_id: int):
    return db.query(models.Blog).filter(models.Blog.id == post_id).first()
    

def get_comments(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()


def edit_blog(
    db: Session,
    post_id: str,
    blog: schemas.BlogCreate,
    current_user: models.User = Depends(get_current_user)
):
    if_not_author_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="is not author",
        headers={"WWW-Authenticate": "Bearer"},
    )
    blogModel = db.query(models.Blog).filter(models.Blog.id == post_id).first()
    if current_user.username != blogModel.author_username :
        raise if_not_author_exception
    db.query(models.Blog).filter(models.Blog.id == post_id).update(vars(blog))
    db.commit()
    return {"Message": "Success"}


def delete_blog(
    db: Session,
    post_id: str,
    current_user: models.User = Depends(get_current_user)
):
    not_author_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="is not author",
        headers={"WWW-Authenticate": "Bearer"},
    )
    blogModel = db.query(models.Blog).filter(models.Blog.id == post_id).first()
    if current_user.username != blogModel.author_username :
        raise not_author_exception
    db.delete(blogModel)
    db.commit()
    return {"Message": "Success"}
