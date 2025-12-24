from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price_at_order: float

class OrderItemResponse(OrderItemCreate):
    id: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    total_amount: float
    payment_mode: str  # COD or ONLINE
    note: Optional[str] = None
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    customer_phone: str
    delivery_address: str
    total_amount: float
    payment_mode: str
    status: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
