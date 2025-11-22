from fastapi import APIRouter

from app.api.endpoints import auth, users, restaurants, orders, employees, requests, notifications, time_clock, service_requests, reports, menu

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(time_clock.router, prefix="/time-clock", tags=["time-clock"])
api_router.include_router(service_requests.router, prefix="/service-requests", tags=["service-requests"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
