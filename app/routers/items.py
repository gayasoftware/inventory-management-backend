from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas, database
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

@router.get("/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_admin_user)):
    return crud.create_item(db=db, item=item)

@router.get("/categories", response_model=List[schemas.Category])
def read_categories(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.get_categories(db)

@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_admin_user)):
    return crud.create_category(db=db, category=category)
