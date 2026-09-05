# Handles API routes for creating, reading, updating, and deleting explorers.

from fastapi import APIRouter, HTTPException
from database import read_from_database, write_to_database
import sqlite3
from models import Explorer
from services.explorer_service import explorer_from_row


router = APIRouter(prefix="/explorers")


# Returns all explorers
@router.get("/")
def get_explorer():

    results = read_from_database(
        "SELECT * FROM explorer ORDER BY name COLLATE NOCASE ASC",
        ()
    )

    explorer_list = [explorer_from_row(row) for row in results]

    return {
        "number_of_explorers": len(explorer_list),
        "explorers": explorer_list
    }


# Returns one explorer by ID
@router.get("/{explorer_id}")
def get_explorer_by_id(explorer_id: int):

    results = read_from_database(
        "SELECT * FROM explorer WHERE id = ?",
        (explorer_id,)
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Explorer not found"
        )

    return explorer_from_row(results[0])


# Adds a new explorer
@router.post("/")
def add_explorer(explorer: Explorer):

    try:
        write_to_database(
            """
            INSERT INTO explorer
            (name, title, activity_period, nationality, expedition_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                explorer.name,
                explorer.title,
                explorer.activity_period,
                explorer.nationality,
                explorer.expedition_count
            )
        )

        return {
            "message": f"Explorer {explorer.name} has been added successfully."
        }

    except sqlite3.Error:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while adding explorer"
        )


# Updates an existing explorer
@router.put("/{explorer_id}")
def update_explorer(explorer_id: int, explorer: Explorer):

    try:
        affected_rows = write_to_database(
            """
            UPDATE explorer
            SET name = ?, title = ?, activity_period = ?,
                nationality = ?, expedition_count = ?
            WHERE id = ?
            """,
            (
                explorer.name,
                explorer.title,
                explorer.activity_period,
                explorer.nationality,
                explorer.expedition_count,
                explorer_id
            )
        )

        if affected_rows == 0:
            raise HTTPException(
                status_code=404,
                detail="Explorer not found"
            )

        return {
            "message": f"Explorer with ID {explorer_id} has been updated successfully."
        }

    except sqlite3.Error:
        raise HTTPException(
            status_code=400,
            detail="Error occurred while updating explorer"
        )


# Deletes an existing explorer
@router.delete("/{explorer_id}")
def delete_explorer(explorer_id: int):

    affected_rows = write_to_database(
        "DELETE FROM explorer WHERE id = ?",
        (explorer_id,)
    )

    if affected_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Explorer not found"
        )

    return {
        "message": f"Explorer with ID {explorer_id} has been deleted successfully."
    }