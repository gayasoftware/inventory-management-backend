from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, dependencies
from ..database import get_db
from ..services.inventory import InventoryService

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)

@router.get("/locations/", response_model=List[schemas.InventoryLocation])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    locations = db.query(models.InventoryLocation).offset(skip).limit(limit).all()
    return locations

@router.post("/locations/", response_model=schemas.InventoryLocation)
def create_location(location: schemas.InventoryLocationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_location = models.InventoryLocation(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.post("/stock/add", response_model=schemas.StockLevel)
def add_stock(stock_in: schemas.StockMovementCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    # Helper endpoint to add stock (purchase)
    if stock_in.type != models.TransactionType.purchase:
         raise HTTPException(status_code=400, detail="Only purchase type allowed for this endpoint")
    
    if not stock_in.to_location_id:
        raise HTTPException(status_code=400, detail="to_location_id required")

    return InventoryService.add_stock(
        db, 
        stock_in.sku_id, 
        stock_in.to_location_id, 
        stock_in.quantity, 
        current_user.id
    )

@router.get("/stock/{sku_id}", response_model=int)
def get_stock(sku_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    return InventoryService.get_total_stock(db, sku_id)

@router.get("/stock/", response_model=List[schemas.StockLevel])
def read_stock_levels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    stock_levels = db.query(models.StockLevel).offset(skip).limit(limit).all()
    return stock_levels

@router.post("/stock/", response_model=schemas.StockLevel)
def create_stock_level(stock_level: schemas.StockLevelCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_stock_level = models.StockLevel(**stock_level.dict())
    db.add(db_stock_level)
    db.commit()
    db.refresh(db_stock_level)
    return db_stock_level

@router.get("/movements/", response_model=List[schemas.StockMovement])
def read_stock_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    movements = db.query(models.StockMovement).order_by(models.StockMovement.timestamp.desc()).offset(skip).limit(limit).all()
    return movements
