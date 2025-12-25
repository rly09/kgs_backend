from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
from ..database import get_db
from ..models import Product, Admin
from ..schemas import ProductCreate, ProductUpdate, ProductResponse
from ..auth import get_current_admin

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if available_only:
        query = query.filter(Product.is_available == True)
    
    products = query.all()
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.post("", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
    admin: Admin = Depends(get_current_admin)
):
    """Upload product image"""
    # Log for debugging
    print(f"Received file: {file.filename}")
    print(f"Content type: {file.content_type}")
    
    # Validate file type by extension (more reliable across platforms)
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Get file extension
    file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    
    print(f"File extension: {file_extension}")
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only JPEG, PNG, and WebP images are allowed. Received: {file.filename}"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/products"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )
    
    # Return the image path (will be served as static file)
    return {
        "image_path": f"/uploads/products/{unique_filename}",
        "message": "Image uploaded successfully"
    }
