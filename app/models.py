from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func

# SQLAlchemy model — equivalent of Django's models.Model
# __tablename__ explicitly sets the DB table name
class User(Base):
    __tablename__ = "users"


    # Column() defines a database column
    # Integer, String etc. map to PostgreSQL types
    # primary_key=True = this is the PK, auto-increments
    id = Column(Integer, primary_key=True, index=True)

    # unique=True = PostgreSQL UNIQUE constraint
    # index=True = creates a DB index automatically
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # hashed_password stores the bcrypt hash, never plain text
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # server_default=func.now() = PostgreSQL sets this to NOW() on insert
    # Equivalent of Django's auto_now_add=True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # relationship() sets up the Python-level link between User and Product
    # back_populates creates the reverse relationship on Product
    # Equivalent of Django's related_name
    products = relationship("Product", back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, default="")

    price = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ForeignKey links to users.id — equivalent of Django's ForeignKey
    owner_id = Column(Integer, ForeignKey("users.id"))

    # relationship() sets up the Python-level link to User
    # back_populates creates the reverse relationship on User
    owner = relationship("User", back_populates="products")