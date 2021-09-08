from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACCESS_TOKEN_EXPIRE_MINUTES = 90

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/blogs/api/post_list/", response_model=List[schemas.Blog])
def get_blogs(db: Session = Depends(get_db)):
    blogs = crud.get_blogs(db)
    print(blogs[0].created_at)
    return blogs


@app.get("/blogs/api/post_list/{author}", response_model=List[schemas.Blog])
def get_blogs(author: str,  db: Session = Depends(get_db)):
    blogs = crud.get_blogs(db, author)
    return blogs


@app.get("/blogs/api/comment_detail/{post_id}", response_model=List[schemas.Comment])
def get_comments(post_id: int,  db: Session = Depends(get_db)):
    comments = crud.get_comments(db, post_id)
    return comments


@app.get("/blogs/api/post_detail/{post_id}", response_model=schemas.Blog)
def get_blog_details(post_id: int,  db: Session = Depends(get_db)):
    blog = crud.get_blog_details(db, post_id)
    return blog


@app.post("/blogs/api/register/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.post("/blogs/api/login/", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Returns jwt token on successfull authentication"""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/blogs/api/create_blog/")
async def create_blog(
    blog: schemas.BlogCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(crud.get_current_user)
):
    return await crud.create_blog(db=db, blog=blog, current_user=current_user)


@app.post("/blogs/api/create_comment/{post_id}")
async def create_comment(
    comment: schemas.CommentCreate, 
    post_id: str, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(crud.get_current_user)
):
    return await crud.create_comment(db=db, post_id=post_id, comment=comment, current_user=current_user)


@app.put("/blogs/api/post_edit/{post_id}")
def edit_blog(
    blog: schemas.BlogCreate,
    post_id: int,
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(crud.get_current_user)
):
    message = crud.edit_blog(
        db=db,
        post_id=post_id,
        blog=blog,
        current_user=current_user
        )
    return message


@app.delete("/blogs/api/post_delete/{post_id}")
def delete_blog(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(crud.get_current_user)
):
    message = crud.delete_blog(
        db=db,
        post_id=post_id,
        current_user=current_user
        )
    return message
