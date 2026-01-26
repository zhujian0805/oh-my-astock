"""
Stock Info Router
FastAPI router for individual stock information endpoints
"""

import logging
import re
from typing import Dict
import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ..services.stock_info_service import StockInfoService

logger = logging.getLogger(__name__)

router = APIRouter()
service = StockInfoService()


class StockInfoResponse(BaseModel):
    """Stock information response model."""
    stock_code: str = Field(..., description="The 6-digit stock code requested")
    data: Dict[str, str] = Field(..., description="Merged stock information as key-value pairs")
    source_status: Dict[str, str] = Field(..., description="Status of each data source")
    timestamp: str = Field(..., description="When the data was last fetched")
    cache_status: str = Field(..., description="Indicates if data is fresh, cached, or stale")


@router.get("/stocks/{stock_code}/info", response_model=StockInfoResponse)
async def get_stock_info(stock_code: str) -> StockInfoResponse:
    """
    Get merged individual stock information

    - **stock_code**: 6-digit stock code (e.g., 000001)
    - Returns merged data from East Money and Xueqiu APIs
    """
    # Validate stock code format
    if not re.match(r'^\d{6}$', stock_code):
        logger.warning(f"Invalid stock code format: {stock_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stock code format"
        )

    try:
        result = service.get_stock_info(stock_code)

        # Add timestamp and cache status to response
        result["timestamp"] = datetime.datetime.now().isoformat()
        result["cache_status"] = "fresh"  # TODO: implement proper cache status detection

        # Check if we got any meaningful data
        has_meaningful_data = bool(result["data"]) and any(
            value and value != "None" for value in result["data"].values()
        )
        if not has_meaningful_data:
            logger.warning(f"No meaningful data found for stock {stock_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not available"
            )

        logger.info(f"Successfully returned stock info for {stock_code}")
        return StockInfoResponse(**result)

    except ValueError as e:
        # Handle invalid stock codes (wrong exchange prefix)
        logger.warning(f"Invalid stock code: {stock_code} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock data not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stock info for {stock_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )