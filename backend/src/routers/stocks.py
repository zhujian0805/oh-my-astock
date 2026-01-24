"""
Stock API routers
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from ..services.stock_service import stock_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stocks")
async def get_all_stocks(
    limit: int = Query(50, ge=1, le=10000),
    offset: int = Query(0, ge=0)
):
    """Get all available stocks with pagination"""
    try:
        stocks = await stock_service.get_all_stocks()

        # Apply pagination
        total = len(stocks)
        paginated_stocks = stocks[offset:offset + limit]

        return {
            "data": paginated_stocks,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

    except Exception as e:
        logger.error(f"Error in get_all_stocks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stocks/{code}/historical")
async def get_historical_data(
    code: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get historical data for a specific stock"""
    try:
        logger.info(f"Historical data request: {code}", extra={
            "start_date": start_date,
            "end_date": end_date
        })

        # Validate stock code format
        if not stock_service.is_valid_stock_code(code):
            logger.warning(f"Invalid stock code format: {code}")
            raise HTTPException(
                status_code=400,
                detail="Invalid stock code format. Expected 6-digit code."
            )

        # Get historical data
        data = await stock_service.get_historical_data(code, start_date, end_date)

        # Stock not found
        if data is None:
            logger.warning(f"Stock not found: {code}")
            raise HTTPException(
                status_code=404,
                detail=f"Stock with code {code} not found"
            )

        logger.info(f"Returning {len(data)} historical records for {code}", extra={
            "date_range": {"start": start_date, "end": end_date} if start_date or end_date else None,
            "data_points": len(data)
        })

        # Return data
        return {
            "stock_code": code,
            "data": data,
            "metadata": {
                "count": len(data),
                "date_range": {"start": start_date, "end": end_date} if start_date or end_date else None,
                "filtered": bool(start_date or end_date)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_historical_data for {code}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")