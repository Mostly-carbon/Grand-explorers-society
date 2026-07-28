import sqlite3

connection = sqlite3.connect('explorer.db')
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id INTEGER PRIMARY KEY,
        name TEXT, scientific_name TEXT,
        kingdom TEXT,
        rarity TEXT,
        habitat TEXT,
        lifespan TEXT,
        diet TEXT,
        description TEXT
    )
""")

connection.commit()
connection.close()

print("Database was created successfully :)")