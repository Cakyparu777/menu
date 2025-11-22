from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String)
    enable_time_clock = Column(Boolean, default=True)
    
    owner = relationship("User", foreign_keys=[owner_id])
    tables = relationship("Table", back_populates="restaurant")
    categories = relationship("Category", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    table_number = Column(String)
    qr_code_url = Column(String, nullable=True)

    restaurant = relationship("Restaurant", back_populates="tables")
