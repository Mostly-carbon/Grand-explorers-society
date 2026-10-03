import sqlite3
from pathlib import Path


# Creates and returns a connection to the production database.
def get_db_connection():
    database_path = Path(__file__).resolve().parent / "grand_explorers_society.db"

    connection = sqlite3.connect(database_path)

    # Allows service code to access columns by name.
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# Executes a SELECT query and returns all matching rows.
def read_from_database(query, parameters=()):
    connection = get_db_connection()

    try:
        cursor = connection.execute(query, parameters)
        return cursor.fetchall()

    finally:
        connection.close()


# Executes an INSERT, UPDATE, or DELETE query.
# Returns the number of rows affected.
def write_to_database(query, parameters=()):
    connection = get_db_connection()

    try:
        cursor = connection.execute(query, parameters)
        connection.commit()

        return cursor.rowcount

    finally:
        connection.close()