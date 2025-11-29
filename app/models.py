from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime

class Role(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"

class TransactionType(str, enum.Enum):
    purchase = "purchase"
    sale = "sale"
    transfer = "transfer"
    adjustment = "adjustment"
    return_in = "return_in"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=Role.staff)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="customer")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    label = Column(String) # e.g., "Home", "Work"
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String, index=True)
    country = Column(String, default="India")
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    brand = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="products")
    skus = relationship("SKU", back_populates="product")

class SKU(Base):
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    sku_code = Column(String, unique=True, index=True)
    price = Column(Float)
    cost_price = Column(Float, nullable=True) # For margin calc
    attributes = Column(String, nullable=True) # JSON string e.g. {"size": "M", "color": "Red"}
    reorder_level = Column(Integer, default=10)
    
    product = relationship("Product", back_populates="skus")
    stock_levels = relationship("StockLevel", back_populates="sku")
    order_items = relationship("OrderItem", back_populates="sku")

class InventoryLocation(Base):
    __tablename__ = "inventory_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    type = Column(String) # "store", "warehouse"
    address = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    
    stock_levels = relationship("StockLevel", back_populates="location")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float)
    quantity = Column(Integer, default=0)  # Total stock across locations
    reorder_level = Column(Integer, default=10)
    margin = Column(Float, default=0.0)  # Percentage margin

    category = relationship("Category")

# Transaction model for purchase/sale records
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    type = Column(String)  # purchase, sale
    quantity = Column(Integer)
    price = Column(Float)
    supplier = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class StockLevel(Base):
    __tablename__ = "stock_levels"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"))
    location_id = Column(Integer, ForeignKey("inventory_locations.id"))
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0) # Reserved for pending orders

    sku = relationship("SKU", back_populates="stock_levels")
    location = relationship("InventoryLocation", back_populates="stock_levels")

class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"))
    from_location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=True)
    to_location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=True)
    quantity = Column(Integer)
    type = Column(Enum(TransactionType))
    reference_id = Column(String, nullable=True) # Order ID or PO ID
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    api_key = Column(String, nullable=True)
    base_cost = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=True)
    delivery_partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=True)
    tracking_number = Column(String, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    customer = relationship("User", back_populates="orders")
    shipping_address = relationship("Address")
    order_items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    sku_id = Column(Integer, ForeignKey("skus.id"))
    quantity = Column(Integer)
    price = Column(Float) # Price at time of purchase
    
    order = relationship("Order", back_populates="order_items")
    sku = relationship("SKU", back_populates="order_items")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float)
    method = Column(String) # "card", "upi", "cod"
    status = Column(String) # "pending", "completed", "failed"
    transaction_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payments")
