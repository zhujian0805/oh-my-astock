"""
Stock Information Models
Pydantic models for stock data validation and serialization
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class StockInfoResponse(BaseModel):
    """API response model for stock information"""

    stock_code: str
    data: Dict[str, str]
    source_status: Dict[str, str]
    timestamp: str
    cache_status: str</content>
<parameter name="file_path">backend/src/models/stock_info.py