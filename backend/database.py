import sqlite3
from pathlib import Path

# Creates and returns a connection to the project database
def get_db_connection():
    database_path = Path(__file__).resolve().parent / "explorer.db"
    connection = sqlite3.connect(database_path)
    return sqlite3.connect(database_path)


# Executes a SELECT query and returns all matching rows
def read_from_database(query, parameters):

    connect = get_db_connection()
    cursor = connect.cursor()

    try:
        cursor.execute(query, parameters)
        results = cursor.fetchall()

        connect.close()
        return results

    except sqlite3.Error:
        connect.close()
        raise


# Executes an INSERT, UPDATE, or DELETE query
# Returns the number of rows affected by the operation
def write_to_database(query, parameters):

    connect = get_db_connection()
    cursor = connect.cursor()

    try:
        cursor.execute(query, parameters)
        connect.commit()

        results = cursor.rowcount

        connect.close()
        return results

    except sqlite3.Error:
        connect.close()
        raise