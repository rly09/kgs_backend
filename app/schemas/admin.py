from pydantic import BaseModel
from datetime import datetime

class AdminBase(BaseModel):
    phone: str
    name: str

class AdminCreate(AdminBase):
    password: str

class AdminLogin(BaseModel):
    phone: str
    password: str

class AdminResponse(AdminBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
