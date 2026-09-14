# Handles API routes for creating, reading, updating, deleting, searching, and sorting species.

from fastapi import APIRouter, HTTPException
from database import read_from_database, write_to_database
import sqlite3
from models import Species
from services.species_service import species_from_row


router = APIRouter(prefix="/species")


# Returns all species
@router.get("/")
def get_species():

    results = read_from_database(
        """
        SELECT *
        FROM species
        ORDER BY COALESCE(common_name, scientific_name) COLLATE NOCASE ASC
        """,
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
    common_name: str = None,
    scientific_name: str = None,
    kingdom: str = None,
    rank: str = None,
    taxonomic_status: str = None,
    sort: str = None,
    order: str = "asc"
):

    query = "SELECT * FROM species"
    parameters = []
    conditions = []

    if common_name is not None:
        conditions.append("common_name COLLATE NOCASE LIKE ?")
        parameters.append(f"%{common_name}%")

    if scientific_name is not None:
        conditions.append("scientific_name COLLATE NOCASE LIKE ?")
        parameters.append(f"%{scientific_name}%")

    if kingdom is not None:
        conditions.append("kingdom COLLATE NOCASE = ?")
        parameters.append(kingdom)

    if rank is not None:
        conditions.append("rank COLLATE NOCASE = ?")
        parameters.append(rank)

    if taxonomic_status is not None:
        conditions.append("taxonomic_status COLLATE NOCASE = ?")
        parameters.append(taxonomic_status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    sort_options = {
        "common_name": "common_name",
        "scientific_name": "scientific_name",
        "kingdom": "kingdom",
        "rank": "rank",
        "taxonomic_status": "taxonomic_status"
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
        sort_column = "common_name"

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
            (common_name, scientific_name, kingdom, rank, taxonomic_status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                species.common_name,
                species.scientific_name,
                species.kingdom,
                species.rank,
                species.taxonomic_status
            )
        )

        return {
            "message": f"Species '{species.scientific_name}' has been added successfully."
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
            SET common_name = ?, scientific_name = ?, kingdom = ?,
                rank = ?, taxonomic_status = ?
            WHERE id = ?
            """,
            (
                species.common_name,
                species.scientific_name,
                species.kingdom,
                species.rank,
                species.taxonomic_status,
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