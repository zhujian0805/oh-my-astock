"""
Stock Information API Router

FastAPI router for stock information endpoints.
"""

import logging
from typing import Dict, List, Optional
import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.stock_info_service import StockInfoService

logger = logging.getLogger(__name__)
service = StockInfoService()


class StockInfoResponse(BaseModel):
    """Stock information response model."""
    stock_code: str = Field(..., description="The 6-digit stock code requested")
    data: Dict[str, str] = Field(..., description="Merged stock information as key-value pairs")
    source_status: Dict[str, str] = Field(..., description="Status of each data source")
    timestamp: str = Field(..., description="When the data was last fetched")
    cache_status: str = Field(..., description="Indicates if data is fresh, cached, or stale")


class BatchStockInfoRequest(BaseModel):
    """Batch stock info request model."""
    stock_codes: List[str] = Field(..., min_items=1, max_items=50, description="List of stock codes")
    force_refresh: bool = Field(False, description="Force refresh from APIs")


class BatchStockInfoResponse(BaseModel):
    """Batch stock info response model."""
    results: List[Optional[StockInfoResponse]] = Field(..., description="Stock information results")
    errors: List[Dict] = Field(default_factory=list, description="Error details for failed requests")
    processed_count: int = Field(..., description="Total number of stocks processed")
    success_count: int = Field(..., description="Number of successful requests")
    error_count: int = Field(..., description="Number of failed requests")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[str] = Field(None, description="Additional error details")
    stock_code: Optional[str] = Field(None, description="Related stock code")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get(
    "/{stock_code}/info",
    response_model=StockInfoResponse,
    responses={
        200: {"description": "Successful response with stock information"},
        404: {"description": "Stock not found", "model": ErrorResponse},
        422: {"description": "Invalid stock code format", "model": ErrorResponse},
        503: {"description": "External API unavailable", "model": ErrorResponse}
    }
)
async def get_stock_info(
    stock_code: str = Query(..., pattern=r'^\d{6}$', description="Stock code (6 digits)")
) -> StockInfoResponse:
    """
    Get comprehensive stock information for a single stock.

    Returns merged data from East Money and Xueqiu APIs.
    """
    try:
        # Validate stock code format
        if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
            raise HTTPException(status_code=422, detail={
                "error": "Invalid stock code format",
                "code": "INVALID_STOCK_CODE",
                "details": "Stock code must be 6 digits"
            })

        result = service.get_stock_info(stock_code)

        # Add timestamp and cache status to response
        result["timestamp"] = datetime.datetime.now().isoformat()
        result["cache_status"] = "fresh"  # TODO: implement proper cache status detection

        return StockInfoResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": str(e)
        })


@router.post(
    "/info/batch",
    response_model=BatchStockInfoResponse,
    responses={
        200: {"description": "Successful batch response"},
        400: {"description": "Invalid request parameters", "model": ErrorResponse},
        503: {"description": "External API unavailable", "model": ErrorResponse}
    }
)
async def get_stock_info_batch(request: BatchStockInfoRequest) -> BatchStockInfoResponse:
    """
    Get stock information for multiple stocks in a single request.

    Processes stocks in parallel with rate limiting.
    """
    try:
        # TODO: Implement actual batch processing
        # results = await stock_info_service.get_stock_info_batch(
        #     request.stock_codes,
        #     request.force_refresh
        # )

        # For now, return mock response structure
        raise HTTPException(status_code=503, detail={
            "error": "Batch stock information service not yet implemented",
            "code": "SERVICE_UNAVAILABLE"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch stock info request: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        })