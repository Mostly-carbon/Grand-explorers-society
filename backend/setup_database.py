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

# Insert the first documented species
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

# Save the changes and close the connection
connection.commit()
connection.close()

print("Database was created successfully :)")