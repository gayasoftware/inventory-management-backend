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
def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_item = crud.create_item(db=db, item=item)
    if db_item is None:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    return db_item

@router.put("/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_item = crud.update_item(db, item_id=item_id, item=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_item = crud.delete_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.get("/categories", response_model=List[schemas.Category])
def read_categories(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.get_categories(db)

@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.create_category(db=db, category=category)

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_category = crud.update_category(db, category_id=category_id, category=category)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(category_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_category = crud.delete_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category
