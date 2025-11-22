import requests
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(
    push_token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send a push notification via Expo Push Notification service.
    """
    if not push_token or not push_token.startswith("ExponentPushToken"):
        print(f"[WARN] Invalid push token: {push_token}")
        return False

    message = {
        "to": push_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {},
    }

    try:
        response = requests.post(EXPO_PUSH_URL, json=message, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if "data" in result and len(result["data"]) > 0:
            ticket = result["data"][0]
            if ticket.get("status") == "error":
                print(f"[ERROR] Push notification error: {ticket.get('message')}")
                return False
        
        print(f"[INFO] Push notification sent successfully to {push_token[:20]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send push notification: {str(e)}")
        return False


def create_notification_record(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Create a notification record in the database.
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        body=body,
        data=data
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_user(
    db: Session,
    user_id: int,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Send push notification and create database record.
    """
    # Create database record
    notification = create_notification_record(db, user_id, title, body, data)
    
    # Get user's push token
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.push_token:
        send_push_notification(user.push_token, title, body, data)
    else:
        print(f"[WARN] User {user_id} has no push token")
    
    return notification
