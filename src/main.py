from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logger import setup_logging, get_logger
from .api.auth import router as auth_router
from .api.invoices import router as invoices_router
from .api.webhooks import router as webhooks_router
from .middleware import SubscriptionLimitCheckerMiddleware

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
app.add_middleware(SubscriptionLimitCheckerMiddleware)

# Include routers
app.include_router(auth_router)
app.include_router(invoices_router)
app.include_router(webhooks_router)

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
