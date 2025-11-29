from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, dependencies
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return db_product

@router.post("/{product_id}/skus/", response_model=schemas.SKU)
def create_sku(product_id: int, sku: schemas.SKUCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_sku = models.SKU(**sku.dict(), product_id=product_id)
    db.add(db_sku)
    db.commit()
    db.refresh(db_sku)
    return db_sku

@router.put("/{product_id}/skus/{sku_id}", response_model=schemas.SKU)
def update_sku(product_id: int, sku_id: int, sku: schemas.SKUCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_sku = db.query(models.SKU).filter(models.SKU.id == sku_id, models.SKU.product_id == product_id).first()
    if not db_sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    for key, value in sku.dict().items():
        setattr(db_sku, key, value)

    db.commit()
    db.refresh(db_sku)
    return db_sku

@router.delete("/{product_id}/skus/{sku_id}", response_model=schemas.SKU)
def delete_sku(product_id: int, sku_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_sku = db.query(models.SKU).filter(models.SKU.id == sku_id, models.SKU.product_id == product_id).first()
    if not db_sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    db.delete(db_sku)
    db.commit()
    return db_sku

@router.get("/{product_id}/skus/", response_model=List[schemas.SKU])
def read_skus(product_id: int, db: Session = Depends(get_db)):
    skus = db.query(models.SKU).filter(models.SKU.product_id == product_id).all()
    return skus

@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(models.Category).offset(skip).limit(limit).all()
    return categories

@router.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.dict().items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(dependencies.get_current_active_staff)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return db_category
