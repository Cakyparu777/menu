from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.services.notification_service import notify_user

router = APIRouter()

@router.post("/", response_model=schemas.ServiceRequestResponse)
def create_service_request(
    *,
    db: Session = Depends(get_db),
    request_in: schemas.ServiceRequestCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Create a service request (Call Waiter / Bill)
    """
    # Verify table exists
    table = db.query(models.Table).filter(models.Table.id == request_in.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    service_request = models.ServiceRequest(
        restaurant_id=table.restaurant_id,
        table_id=table.id,
        user_id=current_user.id if current_user else None,
        type=request_in.type,
        note=request_in.note,
        status="pending"
    )
    
    db.add(service_request)
    db.commit()
    db.refresh(service_request)
    
    # Notify restaurant owner and employees
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == table.restaurant_id).first()
    if restaurant:
        # Notify Owner
        notify_user(
            user_id=restaurant.owner_id,
            title="🛎️ New Service Request",
            body=f"Table {table.table_number}: {request_in.type.title()}",
            data={"type": "service_request", "id": service_request.id},
            db=db
        )
        
        # Notify Employees (TODO: Filter by active/clocked-in employees)
        employees = db.query(models.User).filter(
            models.User.restaurant_id == restaurant.id,
            models.User.role == "employee"
        ).all()
        
        for emp in employees:
            notify_user(
                user_id=emp.id,
                title="🛎️ New Service Request",
                body=f"Table {table.table_number}: {request_in.type.title()}",
                data={"type": "service_request", "id": service_request.id},
                db=db
            )
    
    return service_request

@router.get("/restaurant/{restaurant_id}", response_model=List[schemas.ServiceRequestResponse])
def get_restaurant_requests(
    *,
    db: Session = Depends(get_db),
    restaurant_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    status: Optional[str] = None,
) -> Any:
    """
    Get service requests for a restaurant (Owner/Employee)
    """
    # Verify access
    if current_user.role == 'owner':
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
        if not restaurant or restaurant.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == 'employee':
        if current_user.restaurant_id != restaurant_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(models.ServiceRequest).filter(
        models.ServiceRequest.restaurant_id == restaurant_id
    )
    
    if status:
        query = query.filter(models.ServiceRequest.status == status)
    
    # Join with Table to get table number easily if needed, but we can also just fetch
    requests = query.order_by(models.ServiceRequest.created_at.desc()).all()
    
    # Enrich with table number
    for req in requests:
        req.table_number = req.table.table_number if req.table else "Unknown"
        
    return requests

@router.put("/{request_id}/resolve", response_model=schemas.ServiceRequestResponse)
def resolve_request(
    *,
    db: Session = Depends(get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark service request as completed
    """
    request = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    # Verify access
    if current_user.role == 'owner':
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == request.restaurant_id).first()
        if not restaurant or restaurant.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == 'employee':
        if current_user.restaurant_id != request.restaurant_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
    request.status = "completed"
    request.completed_at = datetime.utcnow()
    
    db.add(request)
    db.commit()
    db.refresh(request)
    
    request.table_number = request.table.table_number if request.table else "Unknown"
    return request
