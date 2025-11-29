from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item: schemas.ItemCreate):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        for key, value in item.dict().items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def get_categories(db: Session):
    return db.query(models.Category).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryCreate):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db_category.name = category.name
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    item = db.query(models.Item).filter(models.Item.id == transaction.item_id).first()
    if not item:
        return None
    
    # Update stock
    if transaction.type == models.TransactionType.purchase:
        item.quantity += transaction.quantity
    elif transaction.type == models.TransactionType.sale:
        if item.quantity < transaction.quantity:
            raise ValueError("Insufficient stock")
        item.quantity -= transaction.quantity
    
    db_transaction = models.Transaction(
        item_id=transaction.item_id,
        user_id=user_id,
        type=transaction.type,
        quantity=transaction.quantity,
        price=item.price, # Use current item price
        supplier=transaction.supplier,
        timestamp=models.datetime.utcnow()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def create_order(db: Session, order: schemas.OrderCreate):
    # Calculate total amount
    total = sum(item.quantity * item.price for item in order.order_items)

    db_order = models.Order(
        customer_id=order.customer_id,
        total_amount=total,
        shipping_address_id=getattr(order, 'shipping_address_id', None),
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create order items and reduce stock
    for order_item in order.order_items:
        sku = db.query(models.SKU).filter(models.SKU.id == order_item.sku_id).first()
        # TODO: Implement stock reduction logic
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            sku_id=order_item.sku_id,
            quantity=order_item.quantity,
            price=order_item.price
        )
        db.add(db_order_item)
    db.commit()
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()

def get_customer_orders(db: Session, customer_id: int):
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).all()

def update_order_status(db: Session, order_id: int, status: models.OrderStatus):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order:
        db_order.status = status
        if status == models.OrderStatus.delivered:
            db_order.delivery_date = models.datetime.utcnow()
        db.commit()
        db.refresh(db_order)
    return db_order

# Address CRUD
def create_address(db: Session, address: schemas.AddressCreate, user_id: int):
    db_address = models.Address(**address.dict(), user_id=user_id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_user_addresses(db: Session, user_id: int):
    return db.query(models.Address).filter(models.Address.user_id == user_id).all()

def update_address(db: Session, address_id: int, address: schemas.AddressCreate, user_id: int):
    db_address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.user_id == user_id).first()
    if db_address:
        for key, value in address.dict(exclude_unset=True).items():
            setattr(db_address, key, value)
        db.commit()
        db.refresh(db_address)
    return db_address

def delete_address(db: Session, address_id: int, user_id: int):
    db_address = db.query(models.Address).filter(models.Address.id == address_id, models.Address.user_id == user_id).first()
    if db_address:
        db.delete(db_address)
        db.commit()
    return db_address
