from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Settings, Admin
from ..auth import get_current_admin

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/discount")
def get_discount(db: Session = Depends(get_db)):
    setting = db.query(Settings).filter(Settings.key == "discount_percentage").first()
    if not setting:
        return {"discount_percentage": 0.0}
    return {"discount_percentage": float(setting.value)}

@router.put("/discount")
def update_discount(
    discount: float,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    if discount < 0 or discount > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discount must be between 0 and 100"
        )
    
    setting = db.query(Settings).filter(Settings.key == "discount_percentage").first()
    if setting:
        setting.value = str(discount)
    else:
        setting = Settings(key="discount_percentage", value=str(discount))
        db.add(setting)
    
    db.commit()
    return {"discount_percentage": discount}
