import sqlite3


def get_db_connection():
    return sqlite3.connect("explorer.db")


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
        

