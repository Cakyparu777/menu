from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

# Base schema
class TimeEntryBase(BaseModel):
    notes: Optional[str] = None

# Create schema - for clock in
class TimeEntryCreate(TimeEntryBase):
    pass

# Update schema - for clock out
class TimeEntryUpdate(BaseModel):
    notes: Optional[str] = None

# Response schema
class TimeEntryResponse(TimeEntryBase):
    id: int
    employee_id: int
    restaurant_id: int
    clock_in: datetime
    clock_out: Optional[datetime] = None
    total_hours: Optional[Decimal] = None
    employee_name: Optional[str] = None  # For display
    
    class Config:
        orm_mode = True

# Summary schema
class TimesheetSummary(BaseModel):
    total_hours: Decimal
    total_days: int
    average_hours_per_day: Decimal
    entries: int
