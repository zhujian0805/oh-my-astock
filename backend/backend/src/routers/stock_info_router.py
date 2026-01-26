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
from ..database import db_service

logger = logging.getLogger(__name__)
service = StockInfoService()


class StockListItem(BaseModel):
    """Stock list item model."""
    code: str = Field(..., description="Stock code")
    name: str = Field(..., description="Stock name")
    exchange: str = Field(..., description="Stock exchange")


class StockListResponse(BaseModel):
    """Stock list response model."""
    stocks: List[StockListItem] = Field(..., description="List of available stocks")


class StockInfoResponse(BaseModel):
    """Stock information response model."""
    code: str = Field(..., description="The 6-digit stock code requested")
    name: Optional[str] = Field(None, description="Stock name")
    symbol: Optional[str] = Field(None, description="Stock symbol")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    current_price: Optional[float] = Field(None, description="Current stock price")
    change_percent: Optional[float] = Field(None, description="Daily price change percentage")
    volume: Optional[int] = Field(None, description="Trading volume")
    turnover: Optional[float] = Field(None, description="Turnover amount")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    pb_ratio: Optional[float] = Field(None, description="Price-to-book ratio")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    data_sources: Dict[str, bool] = Field(..., description="Status of each data source")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    last_updated: str = Field(..., description="When the data was last fetched")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[str] = Field(None, description="Additional error details")


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get(
    "",
    response_model=StockListResponse,
    responses={
        200: {"description": "Successful response with stock list"},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_stock_list() -> StockListResponse:
    """
    Get list of available stocks for dropdown selection.
    """
    try:
        # Get stocks from database
        stocks_data = await db_service.get_stock_list()

        # Convert to response format
        stocks = [
            StockListItem(
                code=stock["code"],
                name=stock["name"],
                exchange=stock["exchange"]
            )
            for stock in stocks_data
        ]

        return StockListResponse(stocks=stocks)

    except Exception as e:
        logger.error(f"Error fetching stock list: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": str(e)
        })


@router.get(
    "/{code}",
    response_model=StockInfoResponse,
    responses={
        200: {"description": "Successful response with stock information"},
        400: {"description": "Invalid stock code", "model": ErrorResponse},
        404: {"description": "Stock not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_stock_info(
    code: str = Query(..., pattern=r'^\d{6}$', description="Stock code (6 digits)")
) -> StockInfoResponse:
    """
    Get detailed information for a specific stock.

    Returns merged data from East Money and Xueqiu APIs.
    """
    try:
        # Validate stock code format
        if not code or len(code) != 6 or not code.isdigit():
            raise HTTPException(status_code=400, detail={
                "error": "Invalid stock code format",
                "code": "INVALID_STOCK_CODE",
                "details": "Stock code must be 6 digits"
            })

        result = service.get_stock_info(code)

        # Add timestamp
        result["last_updated"] = datetime.datetime.now().isoformat()

        return StockInfoResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info for {code}: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "details": str(e)
        })