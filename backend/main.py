# Application entry point for the Grand Explorers' Society API.

from fastapi import FastAPI

from routes.species_routes import router as species_router
from routes.taxa_routes import router as taxa_router


app = FastAPI(
    title="Grand Explorers' Society API",
    description="Production API for the Grand Explorers' Society species archive.",
    version="1.0.0",
)


# Production API routes.
app.include_router(species_router)
app.include_router(taxa_router)


@app.get("/")
def root():
    """Return a simple API status message."""

    return {
        "message": "Camp's standing"
    }


# Start from the backend directory with:
# python -m uvicorn main:app --reload