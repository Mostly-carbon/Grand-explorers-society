
def expedition_from_row(row):
    return {
        "id": row[0],
        "name": row[1],
        "leader_id": row[2],
        "start_date": row[3],
        "end_date": row[4],
        "location": row[5],
        "description": row[6],
        "status": row[7]
    }