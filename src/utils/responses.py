from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None, 
    message: str = "Success", 
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create standardized success response"""
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    
    if meta:
        response_data["meta"] = meta
    
    return JSONResponse(content=response_data, status_code=status_code)


def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[Any] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response"""
    response_data = {
        "success": False,
        "message": message
    }
    
    if errors:
        response_data["errors"] = errors
    
    if request_id:
        response_data["request_id"] = request_id
    
    return JSONResponse(content=response_data, status_code=status_code)


def paginated_response(
    items: list,
    total: int,
    page: int,
    size: int,
    message: str = "Data retrieved successfully"
) -> JSONResponse:
    """Create paginated response"""
    meta = {
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
            "has_next": page * size < total,
            "has_prev": page > 1
        }
    }
    
    return success_response(data=items, message=message, meta=meta)