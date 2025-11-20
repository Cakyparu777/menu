from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    price: Decimal
    # We might want to include item details here for display
    
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    restaurant_id: int
    table_id: int

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

from app.schemas.restaurant import Table

class Order(OrderBase):
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItem] = []
    table: Optional[Table] = None

    class Config:
        orm_mode = True
