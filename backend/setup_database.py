# This file creates the database and its initial data.
from pathlib import Path
import sqlite3

# Connect to the society archive
database_path = Path(__file__).resolve().parent / "explorer.db"
connection = sqlite3.connect(database_path)
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

# Create the species table if it doesn't already exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id INTEGER PRIMARY KEY,
        common_name TEXT,
        scientific_name TEXT UNIQUE NOT NULL,
        kingdom TEXT,
        rank TEXT,
        taxonomic_status TEXT
    );
""")

# Create the sources table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        source_type TEXT
    );
""")

# Connect species to the sources used for their records
cursor.execute("""
    CREATE TABLE IF NOT EXISTS species_sources (
        species_id INTEGER NOT NULL,
        source_id INTEGER NOT NULL,
        PRIMARY KEY (species_id, source_id),
        FOREIGN KEY (species_id) REFERENCES species(id),
        FOREIGN KEY (source_id) REFERENCES sources(id)
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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS expedition (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        leader_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        location TEXT,
        description TEXT,
        status TEXT,
        FOREIGN KEY (leader_id) REFERENCES explorer(id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS explorer_expedition (
        explorer_id INTEGER NOT NULL,
        expedition_id INTEGER NOT NULL,
        PRIMARY KEY (explorer_id, expedition_id),
        FOREIGN KEY (explorer_id) REFERENCES explorer(id),
        FOREIGN KEY (expedition_id) REFERENCES expedition(id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovery (
        id INTEGER PRIMARY KEY,
        expedition_id INTEGER NOT NULL,
        species_id INTEGER NOT NULL,
        discovery_date TEXT,
        location TEXT,
        notes TEXT,
        FOREIGN KEY (expedition_id) REFERENCES expedition(id),
        FOREIGN KEY (species_id) REFERENCES species(id)
    );
""")

# Save the changes and close the connection
connection.commit()
connection.close()

print("Database was created successfully :)")