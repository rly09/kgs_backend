from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Order, OrderItem, Product, Admin, Customer
from ..schemas import OrderCreate, OrderUpdate, OrderResponse
from ..auth import get_current_admin, get_current_customer

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer)
):
    # Create order
    db_order = Order(
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        delivery_address=order.delivery_address,
        total_amount=order.total_amount,
        payment_mode=order.payment_mode,
        note=order.note,
        status="PENDING"
    )
    db.add(db_order)
    db.flush()  # Get the order ID
    
    # Create order items
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price_at_order=item.price_at_order
        )
        db.add(db_item)
        
        # Update product stock
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock -= item.quantity
            if product.stock <= 0:
                product.is_available = False
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer)
):
    # Ensure customer can only access their own orders
    if customer.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    db_order.status = order_update.status
    db_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_order)
    return db_order
