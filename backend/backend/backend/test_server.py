"""
Minimal backend server for testing market quotes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import akshare as ak
from datetime import datetime

app = FastAPI(title="Market Quotes Test API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/market-quotes")
async def get_market_quotes(stocks: str = None):
    """Get market quotes for stocks"""
    try:
        if stocks:
            stock_codes = stocks.split(',')
        else:
            stock_codes = ['000001']  # Default stock

        quotes = []
        for stock_code in stock_codes[:1]:  # Just test one stock
            try:
                # Get data from akshare
                df = ak.stock_bid_ask_em(symbol=stock_code)

                # Convert to dict format
                data = {}
                for _, row in df.iterrows():
                    data[row['item']] = row['value']

                # Build quote response
                quote = {
                    "stock_code": stock_code,
                    "stock_name": None,  # Could be looked up
                    "latest_price": data.get('最新'),
                    "change_amount": data.get('涨跌'),
                    "change_percent": data.get('涨幅'),
                    "volume": data.get('总手'),
                    "turnover": data.get('金额'),
                    "bid_price_1": data.get('buy_1'),
                    "bid_volume_1": data.get('buy_1_vol'),
                    "ask_price_1": data.get('sell_1'),
                    "ask_volume_1": data.get('sell_1_vol'),
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "east_money"
                }
                quotes.append(quote)

            except Exception as e:
                quotes.append({
                    "stock_code": stock_code,
                    "error": str(e),
                    "last_updated": datetime.now().isoformat(),
                    "data_source": "east_money"
                })

        return {
            "quotes": quotes,
            "metadata": {
                "total_quotes": len(quotes),
                "last_updated": datetime.now().isoformat(),
                "data_source": "east_money"
            }
        }

    except Exception as e:
        return {
            "quotes": [],
            "metadata": {
                "error": str(e),
                "total_quotes": 0,
                "last_updated": datetime.now().isoformat(),
                "data_source": "east_money"
            }
        }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)