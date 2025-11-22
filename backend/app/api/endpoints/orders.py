from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.db.session import get_db
from app.socket_manager import notify_new_order, notify_order_update
from app.services.notification_service import notify_user
from fastapi import BackgroundTasks

router = APIRouter()

@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: schemas.OrderCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks = None,
) -> Any:
    """
    Create new order (Customer)
    """
    # Calculate total amount and verify items
    total_amount = 0
    order_items = []
    
    for item_in in order_in.items:
        menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == item_in.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item_in.menu_item_id} not found")
        if not menu_item.is_active:
            raise HTTPException(status_code=400, detail=f"Menu item {menu_item.name} is not available")
        
        item_total = menu_item.price * item_in.quantity
        total_amount += item_total
        order_items.append({
            "menu_item_id": item_in.menu_item_id,
            "quantity": item_in.quantity,
            "price": menu_item.price
        })

    order = models.Order(
        restaurant_id=order_in.restaurant_id,
        table_id=order_in.table_id,
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item_data in order_items:
        order_item = models.OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    # Notify restaurant owner about new order
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == order.restaurant_id).first()
    if restaurant:
        notification_service.notify_user(
            db=db,
            user_id=restaurant.owner_id,
            title="🍽️ New Order Received!",
            body=f"Order #{order.id} - ${float(total_amount):.2f}",
            data={"type": "order", "order_id": order.id}
        )
    
    # Convert order to dict/schema for notification
    # We can just send the ID and let the client fetch, or send the whole object.
    # For simplicity, let's send the order ID and status.
    if background_tasks:
        background_tasks.add_task(notify_new_order, order.restaurant_id, {"id": order.id, "status": order.status, "total_amount": order.total_amount})

    return order

@router.get("/my", response_model=List[schemas.Order])
def read_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's orders
    """
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders

@router.get("/restaurant/{restaurant_id}", response_model=List[schemas.Order])
def read_restaurant_orders(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_owner),
) -> Any:
    """
    Get orders for a restaurant (Owner only)
    """
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    orders = db.query(models.Order).filter(models.Order.restaurant_id == restaurant_id).all()
    return orders

@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_employee),
) -> Any:
    """
    Update order status
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify employee belongs to the restaurant
    if current_user.restaurant_id != order.restaurant_id:
        raise HTTPException(status_code=400, detail="Not authorized")

    order.status = status
    db.add(order)
    db.commit()
    db.refresh(order)

    # Notify customer via WebSocket
    # We can't easily use the global sio instance here without circular imports or setup
    # But we can use the notification service for push notifications
    
    # Send Push Notification to Customer
    if order.user_id:
        title = "Order Update 🍽️"
        body = f"Your order is now {status.title()}!"
        
        if status == 'ready':
            body = "Your food is ready! Please wait for it to be served."
        elif status == 'completed':
            body = "Order completed. Thank you for dining with us!"
            
        notification_service.notify_user(
            user_id=order.user_id,
            title=title,
            body=body,
            data={"type": "order_update", "order_id": order.id, "status": status},
            db=db
        )

    return order
