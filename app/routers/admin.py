from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..database import get_db
from ..models import Order, Product, Admin
from ..auth import get_current_admin, get_password_hash, verify_password

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me")
def get_current_admin_info(admin: Admin = Depends(get_current_admin)):
    return {
        "id": admin.id,
        "phone": admin.phone,
        "name": admin.name
    }

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    # Total revenue (delivered orders only)
    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status == "DELIVERED"
    ).scalar() or 0.0
    
    # Today's revenue
    today = datetime.utcnow().date()
    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status == "DELIVERED",
        func.date(Order.created_at) == today
    ).scalar() or 0.0
    
    # Total orders
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    
    # Pending orders
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == "PENDING"
    ).scalar() or 0
    
    # Total products
    total_products = db.query(func.count(Product.id)).scalar() or 0
    
    # Low stock products (stock < 10)
    low_stock_products = db.query(func.count(Product.id)).filter(
        Product.stock < 10
    ).scalar() or 0
    
    return {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products
    }

# Request models
class UpdatePhoneRequest(BaseModel):
    new_phone: str

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.put("/update-phone")
def update_admin_phone(
    request: UpdatePhoneRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Update admin phone number"""
    # Check if phone already exists
    existing_admin = db.query(Admin).filter(
        Admin.phone == request.new_phone,
        Admin.id != admin.id
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already in use"
        )
    
    # Update phone
    admin.phone = request.new_phone
    db.commit()
    db.refresh(admin)
    
    return {
        "message": "Phone number updated successfully",
        "phone": admin.phone
    }

@router.put("/update-password")
def update_admin_password(
    request: UpdatePasswordRequest,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Update admin password"""
    # Verify old password
    if not verify_password(request.old_password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    # Update password
    admin.password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}
