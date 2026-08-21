from fastapi import APIRouter
from fastapi import HTTPException
from database import read_from_database, write_to_database
import sqlite3
from models import Species

# Creates the species router
router = APIRouter(prefix="/species")


# Returns all species
@router.get("/")
def get_species():

    results = read_from_database("SELECT * FROM species ORDER BY name COLLATE NOCASE ASC", ())
        
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

@router.get("/search")
def search_species(
    name: str = None,
    scientific_name: str = None,
    kingdom: str = None,
    rarity: str = None,
    habitat: str = None,
    diet: str = None,
    sort: str = None,
    order: str = "asc"
):

    query = "SELECT * FROM species"
    parameters = []
    conditions = []

    if name is not None:
        conditions.append("name COLLATE NOCASE LIKE ?")
        parameters.append(f"%{name}%")

    if scientific_name is not None:
        conditions.append("scientific_name COLLATE NOCASE LIKE ?")
        parameters.append(f"%{scientific_name}%")

    if kingdom is not None:
        conditions.append("kingdom COLLATE NOCASE = ?")
        parameters.append(kingdom)

    if rarity is not None:
        conditions.append("rarity COLLATE NOCASE = ?")
        parameters.append(rarity)

    if habitat is not None:
        conditions.append("habitat COLLATE NOCASE LIKE ?")
        parameters.append(f"%{habitat}%")

    if diet is not None:
        conditions.append("diet COLLATE NOCASE = ?")
        parameters.append(diet)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    sort_options = {
            "name": "name",
            "scientific_name": "scientific_name",
            "habitat": "habitat"
        }
    
    if sort is not None:
        try:
            sort_column = sort_options[sort]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid sort option: {sort}. Valid options are: {', '.join(sort_options.keys())}")
    else:
        sort_column = "name"
    
    query += f" ORDER BY {sort_column} COLLATE NOCASE"
    if order.lower() == "desc":
        query += " DESC "
    else:
        query += " ASC "

    results = read_from_database(query, parameters)

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
        "number_of_matches": len(species_list),
        "species": species_list
    }

@router.get("/{species_name}")
def get_species_by_name(species_name):

    results = read_from_database("SELECT * FROM species WHERE name COLLATE NOCASE = ?",
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


# Adds a new species to the database
@router.post("/")
def add_species(species: Species):

    try:
        write_to_database(
            "INSERT INTO species (name, scientific_name, kingdom, rarity, habitat, lifespan, diet, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (species.name, species.scientific_name, species.kingdom, species.rarity, species.habitat, species.lifespan, species.diet, species.description)
        )
        return {"message": f"Species '{species.name}' has been added successfully."}
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Species with this name already exists.")


# Updates an existing species
@router.put("/{species_name}")
def update_species(species_name: str, species: Species):
    affected_rows = write_to_database(
        "UPDATE species SET name = ?, scientific_name = ?, kingdom = ?, rarity = ?, habitat = ?, lifespan = ?, diet = ?, description = ? WHERE name = ?",
        (species.name, species.scientific_name, species.kingdom, species.rarity, species.habitat, species.lifespan, species.diet, species.description, species_name )
    )

    if affected_rows == 0:

        raise HTTPException(
            status_code=404,
            detail="Species not found"
            )
    return {"message": f"Species '{species_name}' has been updated successfully."}


# Deletes a species from the database
@router.delete("/{species_name}")
def delete_species(species_name: str):
    affected_rows = write_to_database(
        "DELETE FROM species WHERE name = ?",
        (species_name,)
    )
    if affected_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Species not found"
        )

    return {"message": f"Species '{species_name}' has been deleted successfully."}