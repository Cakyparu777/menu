from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.api import deps
from app.core import security

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_update: schemas.UserProfileUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user profile.
    """
    update_data = profile_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/avatar")
def upload_avatar(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload user avatar.
    For now, we'll just store a placeholder URL.
    In production, you'd upload to S3/CloudStorage.
    """
    # TODO: Implement actual file upload to cloud storage
    # For now, just return a placeholder
    avatar_url = f"/avatars/{current_user.id}/{file.filename}"
    
    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}

@router.get("/me/stats", response_model=schemas.UserStats)
def get_user_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get user statistics (orders, spending, favorites).
    """
    # Get total orders
    total_orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).count()
    
    # Get total spent
    total_spent_result = db.query(
        func.sum(models.Order.total_amount)
    ).filter(
        models.Order.user_id == current_user.id,
        models.Order.status.in_(["completed", "ready", "preparing"])
    ).scalar()
    
    total_spent = float(total_spent_result) if total_spent_result else 0.0
    
    # Get favorite items (most ordered items)
    # This is a simplified version - you might want to make this more sophisticated
    favorite_items = []
    
    return {
        "total_orders": total_orders,
        "total_spent": total_spent,
        "favorite_items": favorite_items
    }

@router.post("/me/change-password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    password_change: schemas.PasswordChange,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change user password.
    """
    # Verify current password
    if not security.verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    # Validate new password length
    if len(password_change.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long"
        )
    
    # Hash and update new password
    current_user.password_hash = security.get_password_hash(password_change.new_password)
    db.add(current_user)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/set-password")
def set_password(
    *,
    db: Session = Depends(deps.get_db),
    password_in: schemas.SetPassword,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Set password for the first time (or when forced).
    """
    if not current_user.force_password_change:
        raise HTTPException(
            status_code=400,
            detail="Password change is not required"
        )

    if len(password_in.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long"
        )

    current_user.password_hash = security.get_password_hash(password_in.new_password)
    current_user.force_password_change = False
    db.add(current_user)
    db.commit()
    
    return {"message": "Password set successfully"}
