from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal

from app import models, schemas
from app.api import deps
from app.db.session import get_db

router = APIRouter()

@router.post("/clock-in", response_model=schemas.TimeEntryResponse)
def clock_in(
    *,
    db: Session = Depends(get_db),
    entry_in: schemas.TimeEntryCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Clock in (Employee only)
    """
    # Check if employee already has an active clock-in
    active_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.employee_id == current_user.id,
        models.TimeEntry.clock_out == None
    ).first()
    
    if active_entry:
        raise HTTPException(
            status_code=400,
            detail="Already clocked in. Please clock out first."
        )
    
    # Verify user has a restaurant_id
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=400,
            detail="Employee not assigned to a restaurant"
        )
    
    # Create new time entry
    time_entry = models.TimeEntry(
        employee_id=current_user.id,
        restaurant_id=current_user.restaurant_id,
        clock_in=datetime.utcnow(),
        notes=entry_in.notes
    )
    
    db.add(time_entry)
    db.commit()
    db.refresh(time_entry)
    
    return time_entry

@router.put("/clock-out", response_model=schemas.TimeEntryResponse)
def clock_out(
    *,
    db: Session = Depends(get_db),
    entry_update: schemas.TimeEntryUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Clock out (Employee only)
    """
    # Find active clock-in entry
    time_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.employee_id == current_user.id,
        models.TimeEntry.clock_out == None
    ).first()
    
    if not time_entry:
        raise HTTPException(
            status_code=404,
            detail="No active clock-in found"
        )
    
    # Set clock out time
    clock_out_time = datetime.utcnow()
    time_entry.clock_out = clock_out_time
    
    # Calculate total hours
    time_diff = clock_out_time - time_entry.clock_in
    total_hours = Decimal(str(time_diff.total_seconds() / 3600))
    time_entry.total_hours = round(total_hours, 2)
    
    # Update notes if provided
    if entry_update.notes:
        time_entry.notes = entry_update.notes
    
    db.add(time_entry)
    db.commit()
    db.refresh(time_entry)
    
    return time_entry

@router.get("/current", response_model=Optional[schemas.TimeEntryResponse])
def get_current_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current active clock-in status
    """
    active_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.employee_id == current_user.id,
        models.TimeEntry.clock_out == None
    ).first()
    
    return active_entry

def convert_requests_to_entries(requests: List[models.EmployeeRequest]) -> List[schemas.TimeEntryResponse]:
    """Convert approved work requests to time entry format"""
    entries = []
    for req in requests:
        # Calculate total hours
        start = req.start_time
        end = req.end_time
        diff = end - start
        total_hours = Decimal(str(diff.total_seconds() / 3600))
        
        entries.append(schemas.TimeEntryResponse(
            id=req.id, # Use request ID (might overlap with time entry IDs but in this mode we only show requests)
            employee_id=req.employee_id,
            restaurant_id=req.restaurant_id,
            clock_in=start,
            clock_out=end,
            total_hours=round(total_hours, 2),
            notes=req.note,
            employee_name=req.employee.name if req.employee else None
        ))
    return entries

@router.get("/my-timesheet", response_model=List[schemas.TimeEntryResponse])
def get_my_timesheet(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Any:
    """
    Get my timesheet with optional date filtering
    """
    # Check if restaurant uses time clock
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == current_user.restaurant_id).first()
    
    if restaurant and not restaurant.enable_time_clock:
        # Use approved work requests as timesheet
        query = db.query(models.EmployeeRequest).filter(
            models.EmployeeRequest.employee_id == current_user.id,
            models.EmployeeRequest.type == 'work',
            models.EmployeeRequest.status == 'approved'
        )
        
        if start_date:
            query = query.filter(models.EmployeeRequest.start_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(models.EmployeeRequest.start_time <= datetime.fromisoformat(end_date))
            
        requests = query.order_by(models.EmployeeRequest.start_time.desc()).all()
        return convert_requests_to_entries(requests)
        
    # Normal time clock mode
    query = db.query(models.TimeEntry).filter(
        models.TimeEntry.employee_id == current_user.id
    )
    
    if start_date:
        query = query.filter(models.TimeEntry.clock_in >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(models.TimeEntry.clock_in <= datetime.fromisoformat(end_date))
    
    entries = query.order_by(models.TimeEntry.clock_in.desc()).all()
    return entries

@router.get("/restaurant/{restaurant_id}/timesheet", response_model=List[schemas.TimeEntryResponse])
def get_restaurant_timesheet(
    *,
    db: Session = Depends(get_db),
    restaurant_id: int,
    current_user: models.User = Depends(deps.get_current_active_owner),
    employee_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Any:
    """
    Get restaurant timesheet (Owner only)
    """
    # Verify ownership
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.id == restaurant_id
    ).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not restaurant.enable_time_clock:
        # Use approved work requests as timesheet
        query = db.query(models.EmployeeRequest).filter(
            models.EmployeeRequest.restaurant_id == restaurant_id,
            models.EmployeeRequest.type == 'work',
            models.EmployeeRequest.status == 'approved'
        )
        
        if employee_id:
            query = query.filter(models.EmployeeRequest.employee_id == employee_id)
        if start_date:
            query = query.filter(models.EmployeeRequest.start_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(models.EmployeeRequest.start_time <= datetime.fromisoformat(end_date))
            
        requests = query.order_by(models.EmployeeRequest.start_time.desc()).all()
        return convert_requests_to_entries(requests)

    # Normal time clock mode
    query = db.query(models.TimeEntry).filter(
        models.TimeEntry.restaurant_id == restaurant_id
    )
    
    if employee_id:
        query = query.filter(models.TimeEntry.employee_id == employee_id)
    if start_date:
        query = query.filter(models.TimeEntry.clock_in >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(models.TimeEntry.clock_in <= datetime.fromisoformat(end_date))
    
    entries = query.order_by(models.TimeEntry.clock_in.desc()).all()
    return entries

@router.get("/summary", response_model=schemas.TimesheetSummary)
def get_timesheet_summary(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Any:
    """
    Get timesheet summary statistics
    """
    # Check if restaurant uses time clock
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == current_user.restaurant_id).first()
    
    if restaurant and not restaurant.enable_time_clock:
        # Use approved work requests
        query = db.query(models.EmployeeRequest).filter(
            models.EmployeeRequest.employee_id == current_user.id,
            models.EmployeeRequest.type == 'work',
            models.EmployeeRequest.status == 'approved'
        )
        
        if start_date:
            query = query.filter(models.EmployeeRequest.start_time >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(models.EmployeeRequest.start_time <= datetime.fromisoformat(end_date))
            
        requests = query.all()
        converted_entries = convert_requests_to_entries(requests)
        
        if not converted_entries:
            return schemas.TimesheetSummary(
                total_hours=Decimal('0.00'),
                total_days=0,
                average_hours_per_day=Decimal('0.00'),
                entries=0
            )
            
        total_hours = sum(entry.total_hours for entry in converted_entries)
        total_days = len(set(entry.clock_in.date() for entry in converted_entries))
        average = total_hours / total_days if total_days > 0 else Decimal('0.00')
        
        return schemas.TimesheetSummary(
            total_hours=Decimal(str(total_hours)),
            total_days=total_days,
            average_hours_per_day=round(Decimal(str(average)), 2),
            entries=len(converted_entries)
        )

    # Normal time clock mode
    query = db.query(models.TimeEntry).filter(
        models.TimeEntry.employee_id == current_user.id,
        models.TimeEntry.clock_out != None  # Only completed entries
    )
    
    if start_date:
        query = query.filter(models.TimeEntry.clock_in >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(models.TimeEntry.clock_in <= datetime.fromisoformat(end_date))
    
    entries = query.all()
    
    if not entries:
        return schemas.TimesheetSummary(
            total_hours=Decimal('0.00'),
            total_days=0,
            average_hours_per_day=Decimal('0.00'),
            entries=0
        )
    
    total_hours = sum(entry.total_hours for entry in entries if entry.total_hours)
    total_days = len(set(entry.clock_in.date() for entry in entries))
    average = total_hours / total_days if total_days > 0 else Decimal('0.00')
    
    return schemas.TimesheetSummary(
        total_hours=Decimal(str(total_hours)),
        total_days=total_days,
        average_hours_per_day=round(Decimal(str(average)), 2),
        entries=len(entries)
    )
