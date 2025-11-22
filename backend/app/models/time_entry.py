from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    clock_in = Column(DateTime(timezone=True), nullable=False, index=True)
    clock_out = Column(DateTime(timezone=True), nullable=True)
    total_hours = Column(Numeric(5, 2), nullable=True)  # Calculated when clocking out
    notes = Column(String, nullable=True)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id])
    restaurant = relationship("Restaurant")
