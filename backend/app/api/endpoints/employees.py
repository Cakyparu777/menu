from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.api import deps
from app.core.security import get_password_hash
from app.models.restaurant import Restaurant
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_employees(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve employees for the current owner's restaurant.
    """
    if current_user.role != "owner":
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).first()
    if not restaurant:
        return []
        
    employees = db.query(User).filter(
        User.restaurant_id == restaurant.id,
        User.role == "employee"
    ).all()
    return employees

@router.post("/", response_model=schemas.User)
def create_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_in: schemas.EmployeeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new employee.
    """
    if current_user.role != "owner":
        raise HTTPException(status_code=400, detail="Not enough permissions")

    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    user = db.query(User).filter(User.email == employee_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # Create employee user
    # We set a random password hash so it can't be used for normal login until set
    # Login endpoint will handle the force_password_change case
    db_obj = User(
        email=employee_in.email,
        password_hash=get_password_hash("TEMPORARY_PASSWORD_CHANGE_ME"), 
        name=employee_in.name,
        phone=employee_in.phone,
        role="employee",
        restaurant_id=restaurant.id,
        force_password_change=True,
        is_active=True,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
