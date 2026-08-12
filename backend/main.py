from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from database import get_db_connection, read_from_database, write_to_database 

# Create the FastAPI application
app = FastAPI()


# Data model used when creating or updating a species
class Species(BaseModel):
    name: str
    scientific_name: str
    kingdom: str
    rarity: str
    habitat: str
    lifespan: str
    diet: str
    description: str


# Root endpoint - confirms that the API is running
@app.get("/")
def root():
    return {"message": "Camp's standing"}


# Returns every documented species
@app.get("/species")
def species():

    results = read_from_database("SELECT * FROM species", ())
    
    # Convert database rows into JSON-friendly dictionaries
    species_list = []

    for row in results:
        species_data = {
            "name": row[1],
            "scientific_name": row[2],
            "kingdom": row[3],
            "rarity": row[4],
            "habitat": row[5],
            "lifespan": row[6],
            "diet": row[7],
            "description": row[8]
        }

        species_list.append(species_data)

    return {
        "number_of_species": len(species_list),
        "species": species_list
    }


# Returns all species matching the requested name
@app.get("/species/{species_name}")
def get_species(species_name):

    results = read_from_database("SELECT * FROM species WHERE name = ?",
                                (species_name,))

    # Convert matching rows into JSON-friendly dictionaries
    species_name_list = []

    for row in results:
        species_data = {
            "name": row[1],
            "scientific_name": row[2],
            "kingdom": row[3],
            "rarity": row[4],
            "habitat": row[5],
            "lifespan": row[6],
            "diet": row[7],
            "description": row[8]
        }

        species_name_list.append(species_data)


    return {
        "number_of_matches": len(species_name_list),
        "species": species_name_list
    }


# Returns information about the Society itself
@app.get("/charter")
def charter():
    return {
        "name": "Grand Explorer's Society",
        "charter": "To discover, document, classify, and preserve knowledge of the world's flora and fauna, with particular attention given to rare, unusual, and previously undocumented species.",
        "founded": 1887
    }

# Adds a new species to the database
@app.post("/species")
def add_species(species: Species):

    try:
        write_to_database("""
                    INSERT INTO species
                    (name, scientific_name, kingdom, rarity,
                    habitat, lifespan, diet, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        species.name,
                        species.scientific_name,
                        species.kingdom,
                        species.rarity,
                        species.habitat,
                        species.lifespan,
                        species.diet,
                        species.description,
                    )
            )
        
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"Species '{species.name}' a douplicate entry already exists in the database"
        )
        

            

    return {"message": f"Species '{species.name}' has been documented"}


# Updates an existing species
@app.put("/species/{species_name}")
def update_species(species_name: str, species: Species):

    affected_rows = write_to_database(
        """
        UPDATE species
        SET
            name = ?,
            scientific_name = ?,
            kingdom = ?,
            rarity = ?,
            habitat = ?,
            lifespan = ?,
            diet = ?,
            description = ?
        WHERE name = ?;
        """,
        (
            species.name,
            species.scientific_name,
            species.kingdom,
            species.rarity,
            species.habitat,
            species.lifespan,
            species.diet,
            species.description,
            species_name
        ),
    )

    if affected_rows == 0:
        raise HTTPException(
        status_code=404,
        detail=f"Species '{species_name}' not found"
    )

    return {"message": f"Species '{species.name}' has been updated"}


# Deletes a species from the database
@app.delete("/species/{species_name}")
def delete_species(species_name: str):

    affected_rows = write_to_database(
        "DELETE FROM species WHERE name = ?;",
        (species_name,)
    )

    if affected_rows == 0:
        raise HTTPException(
        status_code=404,
        detail=f"Species '{species_name}' not found"
    )

    return {"message": f"Species '{species_name}' has been deleted"}

# Start the server with:
# python -m uvicorn main:app --reload