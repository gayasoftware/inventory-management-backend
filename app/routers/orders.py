from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, schemas, database
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == models.Role.customer:
        order.customer_id = current_user.id
    elif current_user.role in [models.Role.admin, models.Role.staff]:
        # Allow staff to create orders for customers
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authorized to create orders")
    
    try:
        return crud.create_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == models.Role.customer:
        orders = crud.get_customer_orders(db, current_user.id)
    else:
        orders = crud.get_orders(db, skip, limit)
    return orders

@router.put("/{order_id}/status")
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.Role.admin, models.Role.staff]:
        raise HTTPException(status_code=403, detail="Not authorized")
    order = crud.update_order_status(db=db, order_id=order_id, status=status_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated"}
