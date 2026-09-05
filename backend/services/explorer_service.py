# Contains reusable functions for processing species data.

def explorer_from_row(row):
    return {
        "id": row[0],
        "name": row[1],
        "title": row[2],
        "activity_period": row[3],
        "nationality": row[4],
        "expedition_count": row[5]
    }