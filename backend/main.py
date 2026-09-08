from fastapi import FastAPI
from routes.species import router as species_routes
from routes.explorer_routes import router as explorer_routes
from routes.expedition_routes import router as expedition_routes

# Create the FastAPI application
app = FastAPI()

# Register the routes
app.include_router(species_routes)
app.include_router(explorer_routes)
app.include_router(expedition_routes)

@app.get("/")
def root():
    return {"message": "Welcome to the Grand Explorers' society!"}

# Start the server with:
# python -m uvicorn main:app --reload
# **Just make sure you are in the backend directory (cd backend)