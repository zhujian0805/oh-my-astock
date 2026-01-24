# Phase 0: Research & Technical Decisions

**Feature**: Backend API Data Access Layer
**Date**: 2026-01-24
**Status**: Completed

## Research Questions

From Technical Context, the following items required research:

1. **NEEDS CLARIFICATION**: Python web framework selection (FastAPI, Flask, Django REST Framework)
2. Best practices for DuckDB integration with async web frameworks
3. CORS configuration patterns for development and production
4. API testing patterns with pytest

## Research Findings

### Decision 1: Web Framework Selection

**Decision**: FastAPI

**Rationale**:
- **Native async support**: Built on ASGI (Starlette + Pydantic), handles 100+ concurrent requests effortlessly with async/await patterns
- **Automatic OpenAPI documentation**: Zero-configuration Swagger UI and ReDoc generation - meets FR-008 and User Story 3 requirements
- **Minimal boilerplate**: 3 endpoints can be implemented in ~50 lines of code
- **Performance**: Benchmarks show 10,000-20,000 req/s with <50ms p95 latency (well under 200ms requirement)
- **Built-in CORS**: Single-line middleware configuration for FR-007
- **Excellent pytest integration**: TestClient works seamlessly with existing pytest setup
- **Type safety**: Pydantic models integrate perfectly with existing dataclass models (Stock, etc.)

**Alternatives Considered**:

1. **Flask**:
   - Rejected because: No native async (WSGI-based), requires manual OpenAPI documentation (flask-smorest), ~3x slower for concurrent workloads, more boilerplate
   - Better for: Legacy systems, simple synchronous APIs

2. **Django REST Framework**:
   - Rejected because: Too heavyweight (requires full Django + ORM), ORM coupling conflicts with DuckDB, higher complexity (class-based views, serializers), slower setup time
   - Better for: Large applications with authentication, permissions, admin interfaces

**Performance Expectations**:
- Throughput: 10,000-20,000 requests/second (single worker)
- Latency: p50 <10ms, p95 <50ms, p99 <100ms
- Concurrent requests: 100+ easily supported
- Memory: ~50-100MB per worker process

**Dependencies Required**:
```toml
fastapi>=0.109.0
uvicorn[standard]>=0.27.0  # ASGI server with performance extras
pydantic>=2.5.0            # Type validation and serialization
httpx>=0.26.0              # For TestClient (dev dependency)
```

### Decision 2: DuckDB Integration Pattern

**Decision**: Synchronous queries with FastAPI's thread pool

**Rationale**:
- DuckDB is not async-native (no async/await support)
- FastAPI automatically runs synchronous operations in a thread pool when using `def` (not `async def`)
- This prevents blocking the event loop while maintaining async benefits for I/O
- Existing DatabaseConnection is thread-safe (thread-local connections from feature 001)

**Pattern**:
```python
# Use synchronous function (def, not async def)
@router.get("/stocks")
def get_stocks():  # FastAPI runs this in thread pool
    db_service = DatabaseService()
    stocks = db_service.get_all_stocks()  # Synchronous DuckDB query
    return stocks
```

**Alternatives Considered**:
- **async def with run_in_executor**: More verbose, same performance
- **Connection pooling**: Unnecessary (DuckDB has thread-local connections)

### Decision 3: CORS Configuration

**Decision**: CORSMiddleware with configurable origins

**Rationale**:
- FastAPI's built-in CORSMiddleware handles preflight requests (OPTIONS)
- Supports wildcard (*) for development, specific origins for production
- Meets FR-007 requirement
- Handles User Story 4 acceptance scenarios

**Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["GET"],  # Read-only API
    allow_headers=["*"],
)
```

**Best Practices**:
- Development: `allow_origins=["http://localhost:5173"]` for frontend dev server
- Production: `allow_origins=["https://yourdomain.com"]` specific domain
- Avoid wildcard (*) in production for security

### Decision 4: API Testing Strategy

**Decision**: FastAPI TestClient with pytest

**Rationale**:
- TestClient uses httpx under the hood (same as requests but async-compatible)
- No need for actual server startup (runs app in-memory)
- Integrates with existing pytest setup
- Supports contract tests (endpoint validation) and integration tests (database queries)

**Pattern**:
```python
# tests/contract/test_api.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_get_stocks():
    response = client.get("/api/stocks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Test Organization**:
- `tests/contract/test_api.py`: Endpoint contracts (status codes, response schemas)
- `tests/integration/test_api_database.py`: Database query validation, data integrity

### Decision 5: Response Schema Design

**Decision**: Pydantic models matching database schema

**Rationale**:
- Pydantic provides automatic validation and serialization
- FastAPI auto-generates OpenAPI schema from Pydantic models
- Field names match database schema (snake_case: `close_price`, not `closePrice`)
- Meets FR-011, FR-012 requirements

**Example**:
```python
class StockResponse(BaseModel):
    code: str
    name: str
    metadata: Optional[dict] = None

class HistoricalDataPoint(BaseModel):
    date: date
    close_price: float
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
```

**Alternatives Considered**:
- **Dataclasses**: Less automatic validation, no OpenAPI integration
- **camelCase field names**: Rejected to maintain consistency with database schema

### Decision 6: Error Handling Pattern

**Decision**: HTTPException with descriptive messages

**Rationale**:
- FastAPI's HTTPException automatically formats error responses
- Meets FR-006 (graceful error handling) and SC-007 (descriptive errors)
- Provides context for debugging without exposing sensitive details

**Pattern**:
```python
@router.get("/stocks/{code}/historical")
def get_historical_data(code: str):
    try:
        data = hist_service.get_historical_data(code)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for stock {code}"
            )
        return data
    except Exception as e:
        logger.error(f"Failed to fetch historical data for {code}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve historical data"
        )
```

**Error Response Format**:
```json
{
  "detail": "No historical data found for stock 000001"
}
```

### Decision 7: Logging Integration

**Decision**: Reuse existing lib/logging.py with request logging middleware

**Rationale**:
- Maintains consistency with existing codebase (Constitution Principle V)
- Meets FR-009 requirement (log all requests)
- Supports debug mode for performance metrics

**Implementation**:
```python
# In routes.py
from lib.logging import get_logger
logger = get_logger(__name__)

@router.get("/stocks")
def get_stocks():
    logger.info("Fetching all stocks")
    # ... implementation
    logger.info(f"Returned {len(stocks)} stocks")
```

**Request Logging Middleware** (optional):
```python
# In main.py
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )
    return response
```

### Decision 8: Health Check Implementation

**Decision**: Database connectivity check + timestamp

**Rationale**:
- Meets FR-008 and User Story 3 requirements
- Provides actionable information for monitoring
- Returns 503 (Service Unavailable) when database unreachable

**Implementation**:
```python
@router.get("/health")
def health_check():
    try:
        db_service = DatabaseService()
        is_connected = db_service.database_exists()
        return {
            "status": "ok" if is_connected else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": is_connected
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )
```

## Technology Stack Summary

After research, the complete technology stack for this feature:

**Core Framework**:
- FastAPI 0.109+ (ASGI web framework)
- Uvicorn 0.27+ (ASGI server)
- Pydantic 2.5+ (data validation)

**Existing Dependencies (Reused)**:
- DuckDB 0.8+ (database)
- Python 3.10+ (runtime)
- pytest 7.0+ (testing)

**Testing**:
- httpx 0.26+ (TestClient dependency)
- pytest (existing)

**Total New Dependencies**: 3 packages (~15MB)

## Implementation Timeline

Based on research findings:

1. **Phase 1: Setup** (2-4 hours)
   - Install FastAPI dependencies
   - Create `src/api/` directory structure
   - Configure CORS and logging

2. **Phase 2: Core Endpoints** (4-6 hours)
   - Implement /api/stocks endpoint
   - Implement /api/stocks/{code}/historical endpoint
   - Implement /api/health endpoint
   - Create Pydantic response models

3. **Phase 3: Testing** (3-5 hours)
   - Write contract tests for all endpoints
   - Write integration tests for database queries
   - Verify CORS configuration with frontend

4. **Phase 4: Documentation** (1-2 hours)
   - Verify OpenAPI/Swagger documentation
   - Create quickstart.md
   - Update README

**Total Estimated Time**: 10-17 hours

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| DuckDB blocking event loop | High performance degradation | Use synchronous route handlers (def, not async def) - FastAPI handles thread pool automatically |
| CORS preflight issues | Frontend integration failure | Test with actual frontend origin, use CORSMiddleware properly |
| Large dataset response times | Exceeds 2s requirement | Monitor query performance, add pagination if needed (out of scope initially) |
| Missing database indexes | Slow queries | Verify existing indexes from feature 001 (already in place) |

## Open Questions Resolved

All technical clarifications from plan.md Technical Context have been resolved:

1. ✅ **Web framework**: FastAPI (performance, async, documentation)
2. ✅ **DuckDB integration**: Synchronous queries in thread pool
3. ✅ **CORS configuration**: CORSMiddleware with configurable origins
4. ✅ **Testing strategy**: pytest + FastAPI TestClient
5. ✅ **Response schema**: Pydantic models matching database schema
6. ✅ **Error handling**: HTTPException with descriptive messages
7. ✅ **Logging**: Reuse existing lib/logging.py
8. ✅ **Health check**: Database connectivity + timestamp

## Next Steps

Proceed to Phase 1: Design & Contracts
- Generate data-model.md (API response entities)
- Generate API contracts (OpenAPI specification)
- Generate quickstart.md (setup and running instructions)
- Update agent context (CLAUDE.md)
