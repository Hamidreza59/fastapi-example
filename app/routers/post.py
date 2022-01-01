from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models, schemas, oauth2
from typing import Optional, List

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.PostResponse)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user)):    
    #cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #(payload.title, payload.content, payload.published))
    #new_post = cursor.fetchone()
    #conn.commit()
    new_post = models.Post(owner_id = current_user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/", response_model= List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    #cursor.execute("""SELECT * FROM posts """)
    #posts = cursor.fetchall()
    #posts = cursor.execute("""SELECT posts.*, COUNT(votes.postt_id) as vote FROM posts LEFT JOIN votes
    # ON posts.id = votes.post_id GROUP BY posts.id """)
    # results = []
    # for post in posts:
    #     results.append(dict(post))
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id,
    isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.get("/{id}", response_model= schemas.PostOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * FROM posts WHERE id = (%s)""", (str(id)))
    #post = cursor.fetchone()
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id,
    isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail=f"Not Found post id: {id}")
    return post

@router.put("/{id}", response_model= schemas.PostResponse)
def edit_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #(post.title, post.content, post.published, str(id)))
   #updated_post = cursor.fetchone()
    #conn.commit()
    updated_post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = updated_post_query.first()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
              detail=f'post with id = {id} does not exist')
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return updated_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""DELETE FROM posts WHERE id =  (%s) RETURNING * """,
    #(str(id)))
    #deleted_post = cursor.fetchone()
    #conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
              detail=f'post with id = {id} does not exist')
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)