from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio
import time
import redis.asyncio as redis

from src.config import settings, chatgroq_client
from src.config.database import get_database
from src.utils.responses import success_response, error_response

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return success_response(
        data={
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        },
        message="Service is running"
    )


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_database)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": 0  # Could measure actual latency
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = {
            "status": "healthy"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # ChatGroq check (lightweight)
    try:
        # Just verify client is configured, don't make actual API call
        if settings.groq_api_key:
            health_status["checks"]["chatgroq"] = {
                "status": "configured",
                "model": settings.groq_model
            }
        else:
            health_status["checks"]["chatgroq"] = {
                "status": "not_configured"
            }
    except Exception as e:
        health_status["checks"]["chatgroq"] = {
            "status": "error",
            "error": str(e)
        }
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(content=health_status, status_code=status_code)
