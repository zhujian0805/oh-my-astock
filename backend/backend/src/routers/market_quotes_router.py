"""
Market Quotes Router
FastAPI router for market quotes endpoints
"""

import logging
import re
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query
from ..services.market_quotes_service import market_quotes_service
from ..models.market_quote import MarketQuotesResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/market-quotes", response_model=MarketQuotesResponse)
async def get_market_quotes(
    stocks: Optional[str] = Query(None, description="Comma-separated list of 6-digit stock codes")
) -> MarketQuotesResponse:
    """
    Get current market quotes for stocks

    - **stocks**: Comma-separated list of stock codes (e.g., "000001,600000,300001")
    - Returns bid-ask data and market information for requested stocks
    """
    # Parse stock codes
    stock_codes = None
    if stocks:
        # Split by comma and validate
        codes = [code.strip() for code in stocks.split(',') if code.strip()]
        if not codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid stocks parameter format"
            )

        # Validate each code format
        invalid_codes = []
        for code in codes:
            if not re.match(r'^\d{6}$', code):
                invalid_codes.append(code)

        if invalid_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock codes: {', '.join(invalid_codes)}. Must be 6 digits each."
            )

        stock_codes = codes

    try:
        # Get quotes from service
        quotes = market_quotes_service.get_market_quotes(stock_codes)

        # Create response
        response = MarketQuotesResponse(
            quotes=quotes,
            metadata={
                "total_quotes": len(quotes),
                "last_updated": datetime.now().isoformat(),
                "data_source": "east_money",
                "requested_stocks": stock_codes or "default"
            }
        )

        logger.info(f"Successfully returned {len(quotes)} market quotes")
        return response

    except Exception as e:
        logger.error(f"Error retrieving market quotes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market quotes"
        )