from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    comments = relationship("Comment", back_populates="commentator")
    blogs = relationship("Blog", back_populates="author")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    author_username = Column(Integer, ForeignKey("users.username"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="blogs")
    

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    commentator_username = Column(Integer, ForeignKey("users.username"))
    post_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"))
    
    post = relationship('Blog', backref=backref('comments_set', cascade="all, delete-orphan"))
    commentator = relationship("User", back_populates='comments')
