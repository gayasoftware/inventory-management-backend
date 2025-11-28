from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .models import Role, TransactionType, OrderStatus

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Role = Role.customer

class User(UserBase):
    id: int
    role: Role

    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int
    delivery_address: str
    status: OrderStatus = OrderStatus.pending

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    order_date: datetime
    total_amount: float
    delivery_date: Optional[datetime] = None
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    # items field removed to prevent recursion loop

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    price: float
    margin: float = 0.0
    quantity: int = 0
    reorder_level: int = 10
    category_id: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    category: Optional[Category] = None

    class Config:
        from_attributes = True

class CategoryWithItems(Category):
    items: List[Item] = []

class TransactionBase(BaseModel):
    item_id: int
    quantity: int
    type: TransactionType
    supplier: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    price: float
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True
