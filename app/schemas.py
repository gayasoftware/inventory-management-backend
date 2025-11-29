from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Role, TransactionType, OrderStatus
import json

# Address Schemas
class AddressBase(BaseModel):
    label: str
    street_address: str
    city: str
    state: str
    pincode: str
    country: str = "India"
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    # addresses will be managed separately, not in update profile

class UserCreate(UserBase):
    password: str
    role: Role = Role.customer

class User(UserBase):
    id: int
    role: Role
    addresses: List[Address] = []

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Item Schemas (kept for compatibility, though models now have Product/SKU)
class ItemBase(BaseModel):
    name: str
    category_id: int
    price: float
    quantity: int
    reorder_level: int = 10
    margin: float = 0.0

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    item_id: int
    quantity: int
    type: str
    price: float
    supplier: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# SKU Schemas
class SKUBase(BaseModel):
    sku_code: str
    price: float
    cost_price: Optional[float] = None
    attributes: Optional[str] = None # JSON string
    reorder_level: int = 10

class SKUCreate(SKUBase):
    pass

class SKU(SKUBase):
    id: int
    product_id: int
    # stock_levels: List['StockLevel'] = []

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    category: Optional[Category] = None
    skus: List[SKU] = []

    class Config:
        from_attributes = True

# Inventory Location Schemas
class InventoryLocationBase(BaseModel):
    name: str
    type: str
    address: Optional[str] = None
    pincode: Optional[str] = None

class InventoryLocationCreate(InventoryLocationBase):
    pass

class InventoryLocation(InventoryLocationBase):
    id: int

    class Config:
        from_attributes = True

# Stock Level Schemas
class StockLevelBase(BaseModel):
    sku_id: int
    location_id: int
    quantity: int
    reserved_quantity: int = 0

class StockLevelCreate(StockLevelBase):
    pass

class StockLevel(StockLevelBase):
    id: int

    class Config:
        from_attributes = True

# Stock Movement Schemas
class StockMovementBase(BaseModel):
    sku_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    quantity: int
    type: TransactionType
    reference_id: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovement(StockMovementBase):
    id: int
    timestamp: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# Delivery Partner Schemas
class DeliveryPartnerBase(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_cost: float = 0.0

class DeliveryPartnerCreate(DeliveryPartnerBase):
    pass

class DeliveryPartner(DeliveryPartnerBase):
    id: int

    class Config:
        from_attributes = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    sku_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    amount: float
    method: str
    status: str
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    order_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    customer_id: int
    shipping_address_id: Optional[int] = None
    delivery_partner_id: Optional[int] = None
    status: OrderStatus = OrderStatus.pending
    total_amount: float

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class Order(OrderBase):
    id: int
    order_date: datetime
    delivery_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    order_items: List[OrderItem] = []
    payments: List[Payment] = []
    shipping_address: Optional[Address] = None

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
