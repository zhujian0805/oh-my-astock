# Quickstart Guide: Backend API Data Access Layer

This guide will help you set up and run the backend API server for the stock market application.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher installed
- Git repository cloned: `oh-my-astock`
- Database initialized via feature 001 (`stocklib init-db --default-db`)
- Database populated with stocks (`stocklib fetch-stocks --default-db`)

## Installation

### 1. Install Dependencies

From the project root directory:

```bash
# Install backend API dependencies
pip install fastapi>=0.109.0 uvicorn[standard]>=0.27.0 pydantic>=2.5.0

# Install testing dependencies (if not already installed)
pip install httpx>=0.26.0 pytest>=7.0.0
```

Or add to `pyproject.toml`:

```toml
[project]
dependencies = [
    # Existing dependencies...
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    # Existing dev dependencies...
    "httpx>=0.26.0",
]
```

Then run:
```bash
pip install -e .
```

### 2. Verify Installation

```bash
python -c "import fastapi; import uvicorn; print('FastAPI installed successfully')"
```

Expected output: `FastAPI installed successfully`

## Running the API Server

### Development Mode (with auto-reload)

From the project root directory:

```bash
# Start the API server on port 8000
uvicorn api.main:app --reload --port 8000

# Or with custom host and port
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/home/user/oh-my-astock']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode (multi-worker)

```bash
# Start with 4 worker processes for production
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use Gunicorn with Uvicorn workers
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Verifying the API

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-24T12:34:56.789Z",
  "database_connected": true
}
```

### 2. List All Stocks

```bash
curl http://localhost:8000/api/stocks
```

Expected response:
```json
[
  {
    "code": "000001",
    "name": "平安银行",
    "metadata": null
  },
  {
    "code": "000002",
    "name": "万科A",
    "metadata": null
  },
  ...
]
```

### 3. Get Historical Data

```bash
curl http://localhost:8000/api/stocks/000001/historical
```

Expected response:
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

## API Documentation

Once the server is running, access the interactive API documentation:

### Swagger UI (recommended for testing)

Open in browser: http://localhost:8000/api/docs

- Interactive API explorer
- Try endpoints directly from browser
- View request/response schemas
- See example payloads

### ReDoc (recommended for reading)

Open in browser: http://localhost:8000/api/redoc

- Clean, readable documentation
- Searchable endpoint list
- Detailed schema descriptions

## Testing the API

### Run Contract Tests

```bash
# From project root
pytest tests/contract/test_api.py -v
```

Expected output:
```
tests/contract/test_api.py::test_health_check PASSED
tests/contract/test_api.py::test_get_stocks PASSED
tests/contract/test_api.py::test_get_historical_data PASSED
tests/contract/test_api.py::test_invalid_stock_code PASSED
```

### Run Integration Tests

```bash
pytest tests/integration/test_api_database.py -v
```

### Run All API Tests

```bash
pytest tests/contract/test_api.py tests/integration/test_api_database.py -v
```

## Frontend Integration

### CORS Configuration

The API is configured to allow requests from the frontend dev server:

- Development origin: `http://localhost:5173` (Vite default)
- Allowed methods: `GET` (read-only API)

### Update Frontend API Base URL

In your frontend code (e.g., `frontend/src/config/api.ts`):

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  stocks: `${API_BASE_URL}/api/stocks`,
  historicalData: (code: string) => `${API_BASE_URL}/api/stocks/${code}/historical`,
  health: `${API_BASE_URL}/api/health`,
};
```

### Test CORS from Frontend

From your frontend application:

```typescript
// Example: Fetch stocks list
const response = await fetch('http://localhost:8000/api/stocks');
const stocks = await response.json();
console.log('Stocks:', stocks);
```

If you see CORS errors, verify:
1. API server is running on port 8000
2. Frontend is running on port 5173
3. CORS middleware is configured in `src/api/main.py`

## Troubleshooting

### Error: "Module not found: api.main"

**Cause**: Python cannot find the `api` module.

**Solution**: Ensure you're running uvicorn from the project root directory where `src/` is located, and that `src/` is in your PYTHONPATH:

```bash
# From project root
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
uvicorn api.main:app --reload
```

Or update `pyproject.toml` to include `src/` in the package:

```toml
[tool.setuptools]
package-dir = {"" = "src"}
```

### Error: "Database not found"

**Cause**: Database file doesn't exist or is not in the expected location.

**Solution**:
```bash
# Initialize the database first
stocklib init-db --default-db

# Populate with stock data
stocklib fetch-stocks --default-db

# Verify database exists
ls -lh data/stocks.duckdb
```

### Error: "CORS policy blocked"

**Cause**: Frontend origin not allowed in CORS configuration.

**Solution**: Update `src/api/main.py` to include your frontend origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

### Performance Issues

**Symptom**: API responses taking >2 seconds.

**Diagnosis**:
```bash
# Check database size
ls -lh data/stocks.duckdb

# Enable debug logging
uvicorn api.main:app --reload --log-level debug

# Monitor query performance
# (Add timing logs to routes.py)
```

**Solutions**:
- Verify database has indexes (created by feature 001)
- Check for large datasets (>10,000 stocks or >5 years historical data)
- Consider pagination for large responses (future enhancement)

## Next Steps

- **Production Deployment**: Set up reverse proxy (nginx), SSL/TLS, process manager (systemd)
- **Monitoring**: Add Prometheus metrics, Sentry error tracking
- **Optimization**: Implement response caching, database connection pooling
- **Features**: Add date range filtering, pagination, additional endpoints

## Quick Reference

### Useful Commands

```bash
# Start dev server
uvicorn api.main:app --reload

# Run tests
pytest tests/contract/test_api.py -v

# Check API health
curl http://localhost:8000/api/health

# View logs
uvicorn api.main:app --reload --log-level debug

# Stop server
Ctrl+C
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/stocks` | GET | List all stocks |
| `/api/stocks/{code}/historical` | GET | Get historical data |
| `/api/docs` | GET | Swagger UI documentation |
| `/api/redoc` | GET | ReDoc documentation |

### Default Ports

- API Server: `8000`
- Frontend Dev Server: `5173` (Vite)
- Database: File-based (no network port)

## Support

For issues or questions:
- Check the [spec.md](./spec.md) for feature requirements
- Review [plan.md](./plan.md) for technical design
- See [data-model.md](./data-model.md) for API response schemas
- Consult [contracts/openapi.yaml](./contracts/openapi.yaml) for full API specification
