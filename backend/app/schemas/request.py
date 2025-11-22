from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .user import User

class RequestBase(BaseModel):
    type: str = "work"
    start_time: datetime
    end_time: datetime
    note: Optional[str] = None

class RequestCreate(RequestBase):
    pass

class RequestUpdate(BaseModel):
    status: str

class RequestResponse(RequestBase):
    id: int
    employee_id: int
    restaurant_id: int
    status: str
    created_at: datetime
    employee: Optional[User] = None

    class Config:
        orm_mode = True
