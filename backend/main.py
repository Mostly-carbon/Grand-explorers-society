from fastapi import FastAPI
from routes.species import router


# Create the FastAPI application
app = FastAPI()

# Register the species routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to the Grand Explorers' society!"}

# Start the server with:
# python -m uvicorn main:app --reload
#...
# Just make sure you are in the backend directory (cd backend)