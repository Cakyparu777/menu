from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    role = Column(String, default="customer") # customer, owner
    is_active = Column(Boolean, default=True)
    
    # Profile fields
    avatar_url = Column(String, nullable=True)
    dietary_preferences = Column(JSON, default=list)  # ["vegetarian", "gluten-free", etc.]
    notification_enabled = Column(Boolean, default=True)
    preferred_language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Employee fields
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    force_password_change = Column(Boolean, default=False)
    
    # Push notification
    push_token = Column(String, nullable=True)
    
    # Relationships
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
