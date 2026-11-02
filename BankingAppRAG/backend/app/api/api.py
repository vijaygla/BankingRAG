from fastapi import APIRouter
from app.api.routers import auth, customer, staff, admin, chat, ingest, system

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(customer.router, prefix="")
api_router.include_router(staff.router, prefix="")
api_router.include_router(admin.router, prefix="")
api_router.include_router(chat.router, prefix="")
api_router.include_router(ingest.router, prefix="")
api_router.include_router(system.router, prefix="")
