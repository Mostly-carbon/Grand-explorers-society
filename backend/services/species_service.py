# Contains reusable functions for processing species data.

def species_from_row(row):
    
    return {
        "id": row[0],
        "common_name": row[1],
        "scientific_name": row[2],
        "kingdom": row[3],
        "rank": row[4],
        "taxonomic_status": row[5]
    }