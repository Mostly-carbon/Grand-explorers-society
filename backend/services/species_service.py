# Contains reusable functions for processing species data.

def species_from_row(row):
    return {
        "id": row[0],
        "name": row[1],
        "scientific_name": row[2],
        "kingdom": row[3],
        "rarity": row[4],
        "habitat": row[5],
        "lifespan": row[6],
        "diet": row[7],
        "description": row[8]
    }