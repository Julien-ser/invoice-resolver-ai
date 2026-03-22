from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    REGISTRY,
    CONTENT_TYPE_LATEST,
)
from starlette.middleware.base import BaseHTTPMiddleware

from .core.config import settings
from .core.logger import setup_logging, get_logger
from .api.auth import router as auth_router
from .api.invoices import router as invoices_router
from .api.webhooks import router as webhooks_router
from .api.ab_testing import router as ab_testing_router
from .api.billing import router as billing_router
from .admin import admin_router
from .middleware import SubscriptionLimitCheckerMiddleware

# Initialize Sentry (if DSN is configured)
if settings.sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0 if settings.debug else 0.1,
            send_default_pii=False,
            integrations=[
                FastApiIntegration(),
                CeleryIntegration(),
            ],
        )
    except ImportError:
        pass  # Sentry not installed, skip

# Prometheus metrics
HTTP_REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        import time

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        HTTP_REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        ).inc()
        HTTP_REQUEST_DURATION.labels(
            method=request.method, path=request.url.path
        ).observe(duration)

        return response


# Setup logging
setup_logging(log_level="INFO", log_file=None)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Autonomous AI agent for resolving invoice disputes and recovering unpaid invoices",
    version="0.1.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add subscription limit checker middleware
app.add_middleware(PrometheusMiddleware)
app.add_middleware(SubscriptionLimitCheckerMiddleware)

# Include routers
app.include_router(auth_router)
app.include_router(invoices_router)
app.include_router(webhooks_router)
app.include_router(ab_testing_router)
app.include_router(billing_router)
app.include_router(admin_router)


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


# Future routers (to be implemented in later tasks)
# app.include_router(invoice_router, prefix="/api/invoices", tags=["invoices"])
# app.include_router(webhook_router, prefix="/api/webhooks", tags=["webhooks"])
# app.include_router(admin_router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.app_name}")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
