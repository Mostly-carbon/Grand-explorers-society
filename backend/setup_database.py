# This file is to setup and create the database for the first time.
import sqlite3
import os

# Connect to the society archive...
connection = sqlite3.connect('explorer.db')
print(os.path.abspath("explorer.db"))
# ...and create a cursor to execute the SQL statements
cursor = connection.cursor()

# Creates the table if it doesn't exist yet
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
# Inserts initial data into the species table
cursor.execute("""
    INSERT INTO species (
        name,
        scientific_name,
        kingdom,
        rarity,
        habitat,
        lifespan,
        diet,
        description
    )
    VALUES (
        'cat',
        'Felis catus',
        'Animal',
        'Common',
        'Domestic',
        '12-18 years',
        'Carnivorous',
        'A small carnivorous mammal'
    );
""")
cursor.execute("""
    INSERT INTO species (
        name,
        scientific_name,
        kingdom,
        rarity,
        habitat,
        lifespan,
        diet,
        description
    )
    
    VALUES (
        'dog',
        'Canis lupus familiaris',
        'Animal',
        'Common',
        'Domestic',
        '10-13 years',
        'Omnivorous',
        'A domesticated carnivore'
    );
""")

cursor.execute("""
    SELECT name, lifespan FROM species;
""")
# Fetches all the results from the executed query
results = cursor.fetchall()
print(results)

# Commits/saves all the changes
connection.commit()
# Closing the database connection
connection.close()

print("Database was created successfully :)")