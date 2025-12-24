from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin, Customer
from ..schemas import AdminLogin, CustomerLogin, TokenResponse
from ..auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/admin/login", response_model=TokenResponse)
def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.phone == credentials.phone).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password"
        )
    
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "admin"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin.id,
            "phone": admin.phone,
            "name": admin.name,
            "type": "admin"
        }
    }

@router.post("/customer/login", response_model=TokenResponse)
def customer_login(credentials: CustomerLogin, db: Session = Depends(get_db)):
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.phone == credentials.phone).first()
    
    # If not, create new customer (auto-register)
    if not customer:
        customer = Customer(
            phone=credentials.phone,
            name=credentials.name
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    access_token = create_access_token(
        data={"sub": str(customer.id), "type": "customer"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": customer.id,
            "phone": customer.phone,
            "name": customer.name,
            "type": "customer"
        }
    }
