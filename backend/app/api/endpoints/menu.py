from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db

router = APIRouter()

# --- Categories ---

@router.post("/categories", response_model=schemas.Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: schemas.CategoryCreate,
    restaurant_id: int, # Passed as query param or body? Let's assume query for now or part of body if nested. 
    # Actually, let's make it part of the body or path. Let's use query param for simplicity or infer from owner.
    # Better: Pass restaurant_id in query param.
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Create new category
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    category = models.Category(
        name=category_in.name,
        restaurant_id=restaurant_id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/{restaurant_id}/categories", response_model=List[schemas.Category])
def read_categories(
    restaurant_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get all categories for a restaurant
    """
    categories = db.query(models.Category).filter(models.Category.restaurant_id == restaurant_id).all()
    return categories

# --- Menu Items ---

@router.post("/items", response_model=schemas.MenuItem)
def create_menu_item(
    *,
    db: Session = Depends(get_db),
    item_in: schemas.MenuItemCreate,
    restaurant_id: int,
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Create new menu item
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    item = models.MenuItem(
        **item_in.dict(),
        restaurant_id=restaurant_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{restaurant_id}/items", response_model=List[schemas.MenuItem])
def read_menu_items(
    restaurant_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get all menu items for a restaurant
    """
    items = db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id).all()
    return items

@router.put("/items/{item_id}", response_model=schemas.MenuItem)
def update_menu_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: schemas.MenuItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Update menu item
    """
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_data = item_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}", response_model=schemas.MenuItem)
def delete_menu_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Delete menu item
    """
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    db.delete(item)
    db.commit()
    return item
