from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter(tags=["posts"])

@router.get("/posts", response_model=List[schemas.Post])
async def read_posts(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    if current_user.is_admin:
        # Admin can see all posts
        return crud.get_posts(db, skip=skip, limit=limit, published_only=published_only)
    else:
        # Regular users can only see published posts
        return crud.get_posts(db, skip=skip, limit=limit, published_only=True)

@router.get("/posts/{post_id}", response_model=schemas.Post)
async def read_post(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if not post.published and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return post

@router.post("/posts", response_model=schemas.Post)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user)
):
    return crud.create_post(db=db, post=post, user_id=current_user.id)

@router.put("/posts/{post_id}", response_model=schemas.Post)
async def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.update_post(db=db, post_id=post_id, post=post)

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin_user)
):
    success = crud.delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}