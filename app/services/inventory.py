from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import StockLevel, StockMovement, SKU, TransactionType, InventoryLocation
from .. import schemas
from fastapi import HTTPException

class InventoryService:
    @staticmethod
    def get_total_stock(db: Session, sku_id: int) -> int:
        """
        Get total available stock (quantity - reserved) for a SKU across all locations.
        """
        result = db.query(
            func.sum(StockLevel.quantity - StockLevel.reserved_quantity)
        ).filter(StockLevel.sku_id == sku_id).scalar()
        return result or 0

    @staticmethod
    def check_stock_availability(db: Session, sku_id: int, requested_qty: int) -> bool:
        total_available = InventoryService.get_total_stock(db, sku_id)
        return total_available >= requested_qty

    @staticmethod
    def reserve_stock(db: Session, sku_id: int, quantity: int, order_id: int = None) -> bool:
        """
        Reserve stock for an order.
        Strategy: First Fit. Find locations with stock and reserve.
        """
        # 1. Get all stock levels for SKU with available stock
        stock_levels = db.query(StockLevel).filter(
            StockLevel.sku_id == sku_id,
            (StockLevel.quantity - StockLevel.reserved_quantity) > 0
        ).all()

        remaining_qty = quantity
        
        # Check if we have enough total stock first
        total_available = sum([(sl.quantity - sl.reserved_quantity) for sl in stock_levels])
        if total_available < quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for SKU {sku_id}")

        for sl in stock_levels:
            available = sl.quantity - sl.reserved_quantity
            if available <= 0:
                continue
            
            to_reserve = min(available, remaining_qty)
            sl.reserved_quantity += to_reserve
            remaining_qty -= to_reserve
            
            if remaining_qty == 0:
                break
        
        if remaining_qty > 0:
            # This shouldn't happen due to the check above, but for safety
            db.rollback()
            raise HTTPException(status_code=500, detail="Error reserving stock")
            
        db.commit()
        return True

    @staticmethod
    def confirm_stock_deduction(db: Session, order_id: int, order_items: list):
        """
        Convert reservation to permanent deduction (Movement).
        This is called when payment is confirmed.
        """
        # This is complex because we need to know WHICH stock level was reserved.
        # For simplicity in this MVP, we will just deduct from reserved and quantity
        # where reserved > 0.
        
        for item in order_items:
            sku_id = item.sku_id
            qty_to_deduct = item.quantity
            
            stock_levels = db.query(StockLevel).filter(
                StockLevel.sku_id == sku_id,
                StockLevel.reserved_quantity > 0
            ).all()
            
            for sl in stock_levels:
                deduct = min(sl.reserved_quantity, qty_to_deduct)
                sl.reserved_quantity -= deduct
                sl.quantity -= deduct
                qty_to_deduct -= deduct
                
                # Log movement
                movement = StockMovement(
                    sku_id=sku_id,
                    from_location_id=sl.location_id,
                    quantity=deduct,
                    type=TransactionType.sale,
                    reference_id=str(order_id)
                )
                db.add(movement)
                
                if qty_to_deduct == 0:
                    break
            
            if qty_to_deduct > 0:
                # Should not happen if reservation worked
                pass 
        
        db.commit()

    @staticmethod
    def release_stock(db: Session, order_items: list):
        """
        Release reserved stock (e.g. order cancelled/timeout).
        """
        for item in order_items:
            sku_id = item.sku_id
            qty_to_release = item.quantity
            
            stock_levels = db.query(StockLevel).filter(
                StockLevel.sku_id == sku_id,
                StockLevel.reserved_quantity > 0
            ).all()
            
            for sl in stock_levels:
                release = min(sl.reserved_quantity, qty_to_release)
                sl.reserved_quantity -= release
                qty_to_release -= release
                
                if qty_to_release == 0:
                    break
        
        db.commit()

    @staticmethod
    def add_stock(db: Session, sku_id: int, location_id: int, quantity: int, user_id: int):
        stock_level = db.query(StockLevel).filter(
            StockLevel.sku_id == sku_id,
            StockLevel.location_id == location_id
        ).first()
        
        if not stock_level:
            stock_level = StockLevel(
                sku_id=sku_id,
                location_id=location_id,
                quantity=0,
                reserved_quantity=0
            )
            db.add(stock_level)
        
        stock_level.quantity += quantity
        
        movement = StockMovement(
            sku_id=sku_id,
            to_location_id=location_id,
            quantity=quantity,
            type=TransactionType.purchase,
            user_id=user_id
        )
        db.add(movement)
        db.commit()
        return stock_level
