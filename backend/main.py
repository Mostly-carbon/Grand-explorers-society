from fastapi import FastAPI
import sqlite3
import os

# Create the FastAPI application
app = FastAPI()


# Root endpoint - confirms that the API is running
@app.get("/")
def root():
    return {"message": "Camp's standing"}


# Returns all documented species from the SQLite database
@app.get("/species")
def species():

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    print(os.path.abspath("explorer.db"))
    cursor = connect.cursor()

    # Retrieve every species stored in the database
    cursor.execute("SELECT * FROM species;")
    
    # Store all returned rows in a Python list
    results = cursor.fetchall()

    # This list will hold the JSON-friendly species dictionaries
    species_list = []

    # Convert each database row into a dictionary
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

        # Add the converted species to the response list
        species_list.append(species_data)

    # Close the database connection after all data has been retrieved
    connect.close()

    # Return the final JSON response to the client
    return {
        "number_of_species": len(species_list),
        "species": species_list
    }


# Returns all species matching the requested name
@app.get("/species/{species_name}")
def get_species(species_name):

    # Open a connection to the explorer database
    connect = sqlite3.connect("explorer.db")
    cursor = connect.cursor()
    print(os.path.abspath("explorer.db"))

    # Search the database for species with the requested name
    cursor.execute(
        "SELECT * FROM species WHERE name = ?;",
        (species_name,)
    )

    results = cursor.fetchall()

    # Convert matching database rows into JSON-friendly dictionaries
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

    # Return all matching species
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