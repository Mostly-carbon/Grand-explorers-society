from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

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

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()

    # Retrieve every species from the database
    cursor.execute("SELECT * FROM species;")
    results = cursor.fetchall()

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

    # Close the database connection
    connect.close()

    return {
        "number_of_species": len(species_list),
        "species": species_list
    }


# Adds a new species to the database
@app.post("/species")
def add_species(species: Species):

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()

    # Insert the new species into the database
    cursor.execute(
        """
        INSERT INTO species
        (name, scientific_name, kingdom, rarity, habitat, lifespan, diet, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            species.name,
            species.scientific_name,
            species.kingdom,
            species.rarity,
            species.habitat,
            species.lifespan,
            species.diet,
            species.description
        )
    )

    # Save the changes
    connect.commit()

    # Close the database connection
    connect.close()

    return {"message": f"Species '{species.name}' has been documented"}


# Updates an existing species
@app.put("/species/{species_name}")
def update_species(species_name: str, species: Species):

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()

    # Update the matching species
    cursor.execute(
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
        )
    )

    # Save the changes
    connect.commit()

    # Close the database connection
    connect.close()

    return {"message": f"Species '{species.name}' has been updated"}


# Deletes a species from the database
@app.delete("/species/{species_name}")
def delete_species(species_name: str):

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()

    # Delete the matching species
    cursor.execute(
        "DELETE FROM species WHERE name = ?;",
        (species_name,)
    )

    # Save the changes
    connect.commit()

    # Close the database connection
    connect.close()

    return {"message": f"Species '{species_name}' has been deleted"}


# Returns all species matching the requested name
@app.get("/species/{species_name}")
def get_species(species_name):

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()

    # Search the database for matching species
    cursor.execute(
        "SELECT * FROM species WHERE name = ?;",
        (species_name,)
    )

    results = cursor.fetchall()

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

    # Close the database connection
    connect.close()

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


# Start the server with:
# python -m uvicorn main:app --reload