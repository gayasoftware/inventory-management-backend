from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, crud
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Subrouter for me
me_router = APIRouter()

@me_router.get("/profile", response_model=schemas.User)
def read_own_profile(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@me_router.put("/profile", response_model=schemas.User)
def update_own_profile(user_update: schemas.UserBase, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    # Only allow updating certain fields (not username, role)
    update_data = user_update.dict(exclude_unset=True, exclude={'username', 'role'})
    for key, value in update_data.items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@me_router.get("/addresses", response_model=List[schemas.Address])
def read_own_addresses(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.get_user_addresses(db, current_user.id)

@me_router.post("/addresses", response_model=schemas.Address)
def create_own_address(address: schemas.AddressCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    # If is_default, unset other defaults
    if address.is_default:
        existing_defaults = crud.get_user_addresses(db, current_user.id)
        for addr in existing_defaults:
            if addr.is_default:
                addr.is_default = False
                db.commit()
    return crud.create_address(db, address, current_user.id)

@me_router.put("/addresses/{address_id}", response_model=schemas.Address)
def update_own_address(address_id: int, address: schemas.AddressCreate, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_address = crud.update_address(db, address_id, address, current_user.id)
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    # If setting default, unset others
    if address.is_default:
        other_addresses = crud.get_user_addresses(db, current_user.id)
        for addr in other_addresses:
            if addr.id != address_id and addr.is_default:
                addr.is_default = False
                db.commit()
    return db_address

@me_router.delete("/addresses/{address_id}")
def delete_own_address(address_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_address = crud.delete_address(db, address_id, current_user.id)
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"message": "Address deleted"}

@me_router.get("/orders", response_model=List[schemas.Order])
def read_own_orders(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(get_current_active_user)):
    return crud.get_customer_orders(db, current_user.id)

router.include_router(me_router, prefix="/me")
