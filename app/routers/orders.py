from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, dependencies
from ..database import get_db
from ..services.order import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_user)):
    return OrderService.create_order(db, order, current_user.id)

@router.get("/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_user)):
    # If staff, show all. If customer, show own.
    if current_user.role in [models.Role.admin, models.Role.staff]:
        orders = db.query(models.Order).offset(skip).limit(limit).all()
    else:
        orders = db.query(models.Order).filter(models.Order.customer_id == current_user.id).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == models.Role.customer and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order

@router.post("/{order_id}/pay", response_model=schemas.Order)
def pay_order(order_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_user)):
    # Verify user owns order
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == models.Role.customer and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    return OrderService.confirm_payment(db, order_id, payment)

@router.post("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_user)):
    return OrderService.cancel_order(db, order_id, current_user.id)
@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Simple status update for now. In real app, might need state machine checks.
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
