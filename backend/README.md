# Stock Market Backend API

Python/FastAPI backend for oh-my-astock stock market application.

## Features

- RESTful API for stock data access
- DuckDB integration for high-performance queries
- CORS enabled for frontend integration
- Comprehensive error handling and logging
- Health check endpoint
- Test coverage with pytest

## Prerequisites

- Python >= 3.10
- DuckDB database with stock data (located at `../data/stocks.duckdb`)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your configuration
```

## Running the Server

### Development Mode (with auto-reload)
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### GET /api/stocks
Get all available stocks for dropdown population.

**Response:**
```json
[
  {
    "code": "000001",
    "name": "平安银行"
  },
  ...
]
```

### GET /api/stocks/:code/historical
Get historical price data for a specific stock.

**Parameters:**
- `code` - 6-digit stock code (e.g., "000001")

**Response:**
```json
{
  "stock_code": "000001",
  "data": [
    {
      "date": "2024-01-15",
      "close_price": 12.35,
      "open_price": 12.10,
      "high_price": 12.50,
      "low_price": 12.00,
      "volume": 15420000,
      "turnover": 189567000.00,
      "amplitude": 4.13,
      "price_change_rate": 2.06,
      "price_change": 0.25,
      "turnover_rate": 1.54
    },
    ...
  ]
}
```

### GET /api/health
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-24T12:34:56.789Z",
  "database_connected": true
}
```

## Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection and utilities
│   ├── main.py            # FastAPI application
│   ├── routers/           # API routes
│   │   ├── stocks.py      # Stock-related endpoints
│   │   └── __init__.py
│   └── services/          # Business logic
│       ├── stock_service.py
│       └── __init__.py
├── tests/                 # Test files (Python/pytest)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8000 | Server port |
| DEBUG | true | Debug mode (true/false) |
| DATABASE_PATH | ../data/stocks.duckdb | Path to DuckDB database |
| CORS_ORIGINS | http://localhost:4142,http://localhost:3000 | Allowed CORS origins |
| LOG_LEVEL | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:4142` (Vite dev server)
- `http://localhost:3000` (Alternative frontend port)

To add more origins, update `CORS_ORIGINS` in `.env`.

## Error Handling

All errors return JSON with the following structure:

```json
{
  "code": "ERROR_CODE",
  "message": "Error message description",
  "status": 400
}
```

HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error
- `503` - Service Unavailable (database issues)

## Development

### Code Style
The project uses ruff for linting and formatting.

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Adding New Endpoints

1. Create router method in `src/routers/`
2. Include router in `src/main.py`
3. Add tests in `tests/`
4. Update this README

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_PATH` points to correct DuckDB file
- Check database file exists and has correct permissions
- Ensure stock tables exist: `stock_name_code`, `stock_historical_data`

### CORS Errors
- Verify frontend origin is in `CORS_ORIGINS` environment variable
- Check browser console for specific CORS error details

### Port Already in Use
- Change `PORT` in `.env` file
- Or kill process using port 8000: `lsof -ti:8000 | xargs kill`

## License

MIT
