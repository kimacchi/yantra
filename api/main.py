"""Yantra API - Main application entry point."""
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    API_CONTACT,
    API_LICENSE,
)
from routers import submissions_router, compilers_router, templates_router
from database import SessionLocal
from templates import seed_templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application with enhanced documentation
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    contact=API_CONTACT,
    license_info=API_LICENSE,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Submissions",
            "description": "Operations for submitting code and retrieving execution results.",
        },
        {
            "name": "Compilers",
            "description": "Operations for managing compiler/runtime configurations and Docker images.",
        },
        {
            "name": "Templates",
            "description": "Operations for browsing and managing Dockerfile templates.",
        },
    ],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Yantra API starting up...")

    # Seed Dockerfile templates
    db = SessionLocal()
    try:
        logger.info("📦 Seeding Dockerfile templates...")
        results = seed_templates(db)

        if results["added"]:
            logger.info(f"✅ Added {len(results['added'])} new templates: {', '.join(results['added'])}")
        if results["skipped"]:
            logger.info(f"⏭️  Skipped {len(results['skipped'])} existing templates")
        if results["errors"]:
            logger.error(f"❌ Errors seeding templates: {results['errors']}")

        total_templates = len(results["added"]) + len(results["skipped"])
        logger.info(f"🎉 Template seeding complete! Total templates available: {total_templates}")

    except Exception as e:
        logger.error(f"❌ Failed to seed templates: {str(e)}")
    finally:
        db.close()

    logger.info("✨ Yantra API ready to serve requests!")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "yantra-api"}


# Include routers
app.include_router(submissions_router)
app.include_router(compilers_router)
app.include_router(templates_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
