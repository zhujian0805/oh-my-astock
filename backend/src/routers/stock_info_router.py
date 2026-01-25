"""
Stock Info Router
FastAPI router for individual stock information endpoints
"""

import logging
import re
from typing import Dict
from fastapi import APIRouter, HTTPException, status
from ..services.stock_info_service import StockInfoService

logger = logging.getLogger(__name__)

router = APIRouter()
service = StockInfoService()


@router.get("/stocks/{stock_code}/info", response_model=Dict)
async def get_stock_info(stock_code: str) -> Dict:
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

        # Check if we got any meaningful data
        has_meaningful_data = bool(result["data"]) and any(
            value != "None" for value in result["data"].values()
        )
        if not has_meaningful_data:
            logger.warning(f"No meaningful data found for stock {stock_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock data not available"
            )

        logger.info(f"Successfully returned stock info for {stock_code}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving stock info for {stock_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )