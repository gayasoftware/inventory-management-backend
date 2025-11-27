from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas, database
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

@router.post("/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.get("/", response_model=list[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.get_transactions(db, skip=skip, limit=limit)
