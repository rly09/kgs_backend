from pydantic import BaseModel
from datetime import datetime

class CustomerBase(BaseModel):
    phone: str
    name: str

class CustomerLogin(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
