# Generic router module for the Databricks app template
# Add your FastAPI routes here

from fastapi import APIRouter

from .mcp_info import router as mcp_info_router
from .prompts import router as prompts_router
from .user import router as user_router

router = APIRouter()
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(prompts_router, prefix='/prompts', tags=['prompts'])
router.include_router(mcp_info_router, prefix='/mcp_info', tags=['mcp'])
