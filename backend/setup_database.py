# This file creates the database and its initial data.
import sqlite3

# Connect to the society archive
connection = sqlite3.connect("explorer.db")
cursor = connection.cursor()

# Create the species table if it doesn't already exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        scientific_name TEXT UNIQUE NOT NULL,
        kingdom TEXT,
        rarity TEXT,
        habitat TEXT,
        lifespan TEXT,
        diet TEXT,
        description TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS explorer (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        activity_period TEXT,
        nationality TEXT,
        expedition_count INTEGER
    );
""")

# Save the changes and close the connection
connection.commit()
connection.close()

print("Database was created successfully :)")