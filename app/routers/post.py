from fastapi import APIRouter, HTTPException, Response, status, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import oauth2
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

## POSTS
@router.get("/", response_model=List[schemas.PostOut])
# @router.get("/")
def get_posts( db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_User), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).all() # See all posts
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() # See all posts
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()  # See all owned posts

    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()
    print(results)
    # return posts
    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts( post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_User)):
    # cursor.execute("""INSERT INTO posts(title,content, published) VALUES (%s,%s,%s) RETURNING *""", (post.title, post.content, post.published)) #f strings are vulnerable to SQL Injections
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(**post.model_dump())
    print(current_user)
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_User)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),)) #f strings are vulnerable to SQL Injections
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    # Show only if user owns the post
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_User)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),)) #f strings are vulnerable to SQL Injections
    # del_post = cursor.fetchone()
    # conn.commit()
    del_post_q = db.query(models.Post).filter(models.Post.id == id)
    del_post = del_post_q.first() 
    
    if not del_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist")
    
    # Delete only if user owns the post
    if del_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    del_post_q.delete(synchronize_session = False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_User)):
    # print(post)
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id))) #f strings are vulnerable to SQL Injections
    # upd_post = cursor.fetchone()
    # conn.commit()
    query_post = db.query(models.Post).filter(models.Post.id == id)
    upd_post= query_post.first()
    
    if not upd_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exist")
    
    # Update only if user owns the post
    if upd_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    query_post.update( post.model_dump(), synchronize_session=False)
    db.commit()
    return query_post.first()