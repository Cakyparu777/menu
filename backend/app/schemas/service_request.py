from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ServiceRequestBase(BaseModel):
    type: str # waiter, bill
    note: Optional[str] = None

class ServiceRequestCreate(ServiceRequestBase):
    table_id: int

class ServiceRequestUpdate(BaseModel):
    status: str

class ServiceRequestResponse(ServiceRequestBase):
    id: int
    restaurant_id: int
    table_id: int
    user_id: Optional[int] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    table_number: Optional[str] = None # Helper for UI

    class Config:
        orm_mode = True
