from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String)

    restaurant = relationship("Restaurant", back_populates="categories")
    items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    category = relationship("Category", back_populates="items")
