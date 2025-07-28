from fastapi import APIRouter   
from routes.document_routes import router as document_router

api_router = APIRouter(prefix="/api")

api_router.include_router(document_router, prefix="/document", tags=["Document"])
