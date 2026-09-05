# Handles API routes for creating, reading, updating, deleting, searching, and sorting species.

from fastapi import APIRouter
from fastapi import HTTPException
from database import read_from_database, write_to_database
import sqlite3
from models import Species
from services.species_service import species_from_row


router = APIRouter(prefix="/species")


# Returns all species
@router.get("/")
def get_species():

    results = read_from_database(
        "SELECT * FROM species ORDER BY name COLLATE NOCASE ASC",
        ()
    )

    species_list = [species_from_row(row) for row in results]

    return {
        "number_of_species": len(species_list),
        "species": species_list
    }


# Searches and sorts species
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
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort option: {sort}. Valid options are: {', '.join(sort_options.keys())}"
            )
    else:
        sort_column = "name"

    query += f" ORDER BY {sort_column} COLLATE NOCASE"

    if order.lower() == "desc":
        query += " DESC"
    elif order.lower() == "asc":
        query += " ASC"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid order option: {order}. Valid options are: asc, desc"
        )

    results = read_from_database(query, parameters)

    species_list = [species_from_row(row) for row in results]

    return {
        "number_of_matches": len(species_list),
        "species": species_list
    }


# Returns one species by ID
@router.get("/{species_id}")
def get_species_by_id(species_id: int):

    results = read_from_database(
        "SELECT * FROM species WHERE id = ?",
        (species_id,)
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Species with this id doesn't exist"
        )

    return species_from_row(results[0])


# Adds a new species
@router.post("/")
def add_species(species: Species):

    try:
        write_to_database(
            """
            INSERT INTO species
            (name, scientific_name, kingdom, rarity, habitat, lifespan, diet, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        return {
            "message": f"Species '{species.name}' has been added successfully."
        }

    except sqlite3.IntegrityError as e:
        if "scientific_name" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Species with this scientific name already exists."
            )
        raise


# Updates an existing species
@router.put("/{species_id}")
def update_species(species_id: int, species: Species):

    try:
        affected_rows = write_to_database(
            """
            UPDATE species
            SET name = ?, scientific_name = ?, kingdom = ?, rarity = ?,
            habitat = ?, lifespan = ?, diet = ?, description = ?
            WHERE id = ?
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
                species_id
            )
        )

        if affected_rows == 0:
            raise HTTPException(
                status_code=404,
                detail="Species not found"
            )

        return {
            "message": f"Species with ID {species_id} has been updated successfully."
        }

    except sqlite3.IntegrityError as e:
        if "scientific_name" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Species with this scientific name already exists."
            )
        raise


# Deletes a species
@router.delete("/{species_id}")
def delete_species(species_id: int):

    affected_rows = write_to_database(
        "DELETE FROM species WHERE id = ?",
        (species_id,)
    )

    if affected_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Species not found"
        )

    return {
        "message": f"Species with ID {species_id} has been deleted successfully."
    }