from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post id {vote.post_id} not exist")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, 
    models.Vote.user_id == current_user.id)
    exist_vote = vote_query.first()
    if vote.dir == 1:
        if exist_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"user {current_user.id} has already vote on post id {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        if not exist_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted vote"}
