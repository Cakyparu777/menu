from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from app.api import deps
from app.models.order import Order, OrderItem
from app.models.menu import MenuItem
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/sales")
def get_sales_report(
    period: str = "week",
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_employee)
):
    """
    Get sales report for a specific period (day, week, month).
    """
    restaurant_id = current_user.restaurant_id
    if not restaurant_id:
         # Fallback for owners who might not have restaurant_id directly on user object in some flows,
         # though get_current_active_employee usually ensures it.
         # For now, assume employee/owner has restaurant_id.
         raise HTTPException(status_code=400, detail="User not associated with a restaurant")

    now = datetime.now()
    
    if period == "day":
        start_date = now - timedelta(days=1)
        # Group by hour
        date_trunc = func.date_trunc('hour', Order.created_at)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
        # Group by day
        date_trunc = func.date_trunc('day', Order.created_at)
    elif period == "month":
        start_date = now - timedelta(days=30)
        # Group by day
        date_trunc = func.date_trunc('day', Order.created_at)
    else:
        raise HTTPException(status_code=400, detail="Invalid period")

    results = db.query(
        date_trunc.label('date'),
        func.sum(Order.total_amount).label('total_sales'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.restaurant_id == restaurant_id,
        Order.created_at >= start_date,
        Order.status == 'completed' # Only count completed orders
    ).group_by(
        'date'
    ).order_by(
        'date'
    ).all()

    return [
        {
            "date": r.date,
            "total_sales": float(r.total_sales or 0),
            "order_count": r.order_count
        }
        for r in results
    ]

@router.get("/popular-items")
def get_popular_items(
    limit: int = 5,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_employee)
):
    """
    Get top selling items.
    """
    restaurant_id = current_user.restaurant_id
    
    results = db.query(
        MenuItem.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * OrderItem.price).label('total_revenue')
    ).join(
        OrderItem, MenuItem.id == OrderItem.menu_item_id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(
        Order.restaurant_id == restaurant_id,
        Order.status == 'completed'
    ).group_by(
        MenuItem.id, MenuItem.name
    ).order_by(
        desc('total_quantity')
    ).limit(limit).all()

    return [
        {
            "name": r.name,
            "total_quantity": r.total_quantity,
            "total_revenue": float(r.total_revenue or 0)
        }
        for r in results
    ]

@router.get("/peak-hours")
def get_peak_hours(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_employee)
):
    """
    Get average order volume by hour of day (0-23).
    """
    restaurant_id = current_user.restaurant_id
    
    # Look back 30 days for a good average
    start_date = datetime.now() - timedelta(days=30)

    results = db.query(
        extract('hour', Order.created_at).label('hour'),
        func.count(Order.id).label('order_count')
    ).filter(
        Order.restaurant_id == restaurant_id,
        Order.created_at >= start_date
    ).group_by(
        'hour'
    ).order_by(
        'hour'
    ).all()

    return [
        {
            "hour": int(r.hour),
            "order_count": r.order_count
        }
        for r in results
    ]
