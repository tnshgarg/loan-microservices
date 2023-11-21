

from fastapi import APIRouter
from kyc_service.services.ewa.apollo.router import apollo_ewa_router

ewa_router = APIRouter()

ewa_router.include_router(
    apollo_ewa_router,
    prefix="/apollo"
)
