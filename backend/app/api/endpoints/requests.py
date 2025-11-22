from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.api import deps
from app.models.request import EmployeeRequest, RequestStatus, RequestType
from app.services import notification_service

router = APIRouter()

@router.post("/", response_model=schemas.RequestResponse)
def create_request(
    *,
    db: Session = Depends(deps.get_db),
    request_in: schemas.RequestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new work or leave request.
    """
    if current_user.role != "employee":
        raise HTTPException(status_code=400, detail="Only employees can create requests")

    if not current_user.restaurant_id:
        raise HTTPException(status_code=400, detail="Employee not assigned to a restaurant")

    request = EmployeeRequest(
        employee_id=current_user.id,
        restaurant_id=current_user.restaurant_id,
        type=request_in.type,
        start_time=request_in.start_time,
        end_time=request_in.end_time,
        note=request_in.note,
        status=RequestStatus.PENDING
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Notify owner
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == current_user.restaurant_id).first()
    if restaurant:
        date_str = request_in.start_time.strftime('%Y-%m-%d')
        request_type = "Work" if request_in.type == RequestType.WORK else "Leave"
        notification_service.notify_user(
            db=db,
            user_id=restaurant.owner_id,
            title=f"New Request from {current_user.name}",
            body=f"{request_type} request for {date_str}",
            data={"type": "request", "request_id": request.id}
        )
    
    return request

@router.get("/", response_model=List[schemas.RequestResponse])
def read_requests(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List requests.
    Owner: All requests for their restaurant.
    Employee: Only their own requests.
    """
    if current_user.role == "owner":
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.owner_id == current_user.id).first()
        if not restaurant:
            return []
        requests = db.query(EmployeeRequest).filter(EmployeeRequest.restaurant_id == restaurant.id).all()
    else:
        requests = db.query(EmployeeRequest).filter(EmployeeRequest.employee_id == current_user.id).all()
    return requests

@router.put("/{request_id}", response_model=schemas.RequestResponse)
def update_request_status(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    status_in: schemas.RequestUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update request status (Approve/Reject). Owner only.
    """
    if current_user.role != "owner":
        raise HTTPException(status_code=400, detail="Not enough permissions")

    request = db.query(EmployeeRequest).filter(EmployeeRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify owner owns the restaurant
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.owner_id == current_user.id).first()
    if not restaurant or request.restaurant_id != restaurant.id:
        raise HTTPException(status_code=400, detail="Not authorized to manage this request")

    old_status = request.status
    request.status = status_in.status
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Notify employee if status changed
    if old_status != status_in.status and status_in.status in [RequestStatus.APPROVED, RequestStatus.REJECTED]:
        date_str = request.start_time.strftime("%Y-%m-%d")
        request_type = "work" if request.type == RequestType.WORK else "leave"
        status_text = "approved" if status_in.status == RequestStatus.APPROVED else "declined"
        notification_service.notify_user(
            db=db,
            user_id=request.employee_id,
            title=f"Request {status_text.title()}",
            body=f"Your {request_type} request for {date_str} was {status_text}",
            data={"type": "request", "request_id": request.id, "status": status_text}
        )
    
    return request

@router.get("/schedule", response_model=List[schemas.RequestResponse])
def read_schedule(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get approved requests for the calendar (both work and leave).
    """
    from sqlalchemy.orm import joinedload
    
    if current_user.role == "owner":
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.owner_id == current_user.id).first()
        if not restaurant:
            return []
        restaurant_id = restaurant.id
    else:
        restaurant_id = current_user.restaurant_id

    if not restaurant_id:
        return []

    requests = db.query(EmployeeRequest).options(
        joinedload(EmployeeRequest.employee)
    ).filter(
        EmployeeRequest.restaurant_id == restaurant_id,
        EmployeeRequest.status == RequestStatus.APPROVED
    ).all()
    
    print(f"[DEBUG] Schedule endpoint: Found {len(requests)} approved requests for restaurant {restaurant_id}")
    for req in requests:
        print(f"[DEBUG] Request {req.id}: type={req.type}, date={req.start_time}, status={req.status}")
    
    return requests
