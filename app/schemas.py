from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .models import Role, TransactionType

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: Role = Role.staff

class User(UserBase):
    id: int
    role: Role

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ItemBase(BaseModel):
    name: str
    price: float
    quantity: int = 0
    reorder_level: int = 10
    category_id: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    category: Optional['Category'] = None

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    items: List[Item] = []

    class Config:
        from_attributes = True

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

Item.model_rebuild()
