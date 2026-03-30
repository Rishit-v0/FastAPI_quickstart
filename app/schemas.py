from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Pydantic schemas = DRF Serializers in Django
# They validate incoming request data and shape outgoing response data
# BaseModel is Pydantic's base class — all schemas inherit from it


# UserCreate = what the client sends when registering
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    password2: str

# UserResponse = what the server sends back when a user is created
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    # Config class tells Pydantic to read data from ORM objects
    # Without this, Pydantic can't read SQLAlchemy model attributes
    # Equivalent of DRF's ModelSerializer Meta class with model = User and fields = '__all__'
    class Config:
        from_attributes = True  # Tells Pydantic to work with ORM objects (like SQLAlchemy models)


# Token = what we return after successful login
class Token(BaseModel):
    access_token: str
    token_type: str

# TokenData = what we decode from the JWT token
class TokenData(BaseModel):
    email: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    stock: int = 0

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    is_active: bool
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

