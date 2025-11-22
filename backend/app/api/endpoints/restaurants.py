from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.utils.qr import generate_qr_code

router = APIRouter()

@router.post("/", response_model=schemas.Restaurant)
def create_restaurant(
    *,
    db: Session = Depends(get_db),
    restaurant_in: schemas.RestaurantCreate,
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Create new restaurant (Owner only)
    """
    # Check if owner already has a restaurant (optional constraint)
    # existing = db.query(models.Restaurant).filter(models.Restaurant.owner_id == current_user.id).first()
    # if existing:
    #     raise HTTPException(status_code=400, detail="User already owns a restaurant")

    restaurant = models.Restaurant(
        **restaurant_in.dict(),
        owner_id=current_user.id
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

@router.get("/me", response_model=List[schemas.Restaurant])
def read_my_restaurants(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Get current user's restaurants
    """
    restaurants = db.query(models.Restaurant).filter(models.Restaurant.owner_id == current_user.id).all()
    return restaurants

@router.get("/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get restaurant by ID (Public)
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.put("/{restaurant_id}", response_model=schemas.Restaurant)
def update_restaurant(
    restaurant_id: int,
    restaurant_in: schemas.RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Update restaurant (Owner only)
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_data = restaurant_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

@router.post("/{restaurant_id}/tables", response_model=schemas.Table)
def create_table(
    restaurant_id: int,
    table_in: schemas.TableCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Create a table and generate QR code
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    table = models.Table(
        restaurant_id=restaurant_id,
        table_number=table_in.table_number
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    # Generate QR Code
    # Format: https://<domain>/scan?restaurant_id=1&table_id=1
    qr_data = f"restaurant_id={restaurant_id}&table_id={table.id}"
    qr_code = generate_qr_code(qr_data)
    
    table.qr_code_url = qr_code # Storing base64 for simplicity, ideally upload to S3
    db.add(table)
    db.commit()
    db.refresh(table)
    
    return table

@router.delete("/{restaurant_id}/tables/{table_id}", response_model=schemas.Table)
def delete_table(
    restaurant_id: int,
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Delete a table
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.restaurant_id == restaurant_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(table)
    db.commit()
    return table

@router.put("/{restaurant_id}/tables/{table_id}", response_model=schemas.Table)
def update_table(
    restaurant_id: int,
    table_id: int,
    table_in: schemas.TableUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Update a table (coordinates, etc)
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.restaurant_id == restaurant_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    update_data = table_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(table, field, value)

    db.add(table)
    db.commit()
    db.refresh(table)
    return table
