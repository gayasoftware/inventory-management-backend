from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class Role(str, enum.Enum):
    admin = "admin"
    staff = "staff"

class TransactionType(str, enum.Enum):
    purchase = "purchase"
    sale = "sale"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=Role.staff)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float)
    margin = Column(Float, default=0.0)
    quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)

    category = relationship("Category", back_populates="items")
    transactions = relationship("Transaction", back_populates="item")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) # purchase or sale
    quantity = Column(Integer)
    price = Column(Float) # Unit price at time of transaction
    supplier = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="transactions")
    user = relationship("User")
