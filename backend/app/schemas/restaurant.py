from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal

# --- MenuItem Schemas ---
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    is_active: bool = True
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    category_id: int

class MenuItemUpdate(MenuItemBase):
    category_id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: Optional[bool] = None

class MenuItem(MenuItemBase):
    id: int
    restaurant_id: int
    category_id: int

    class Config:
        orm_mode = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    restaurant_id: int
    items: List[MenuItem] = []

    class Config:
        orm_mode = True

# --- Table Schemas ---
class TableBase(BaseModel):
    table_number: str

class TableCreate(TableBase):
    pass

class Table(TableBase):
    id: int
    restaurant_id: int
    qr_code_url: Optional[str] = None

    class Config:
        orm_mode = True

# --- Restaurant Schemas ---
class RestaurantBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    enable_time_clock: bool = True

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    tables: List[Table] = []
    categories: List[Category] = []

    class Config:
        orm_mode = True
