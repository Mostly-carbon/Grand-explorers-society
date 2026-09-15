# Handles external data ingestion and preparation for the database.

import requests

from models import Species
from database import read_from_database, write_to_database


COL_API_URL = "https://api.checklistbank.org/dataset/3LXR/nameusage/search"


def get_species_from_col(scientific_name):
    response = requests.get(
        COL_API_URL,
        params={"q": scientific_name}
    )

    response.raise_for_status()

    return response.json()


def normalize_species(col_record):
    usage = col_record["usage"]
    name = usage["name"]

    kingdom = next(
        item["name"]
        for item in col_record["classification"]
        if item["rank"] == "kingdom"
    )

    return {
        "common_name": None,
        "scientific_name": name["scientificName"],
        "kingdom": kingdom,
        "rank": name["rank"],
        "taxonomic_status": usage["status"]
    }


def prepare_species(col_record):
    normalized_data = normalize_species(col_record)
    return Species(**normalized_data)


def save_species(species):
    existing = read_from_database(
        "SELECT id FROM species WHERE scientific_name = ?",
        (species.scientific_name,)
    )

    if existing:
        return {
            "status": "already_exists",
            "scientific_name": species.scientific_name,
            "id": existing[0][0]
        }

    write_to_database(
        """
        INSERT INTO species
        (common_name, scientific_name, kingdom, rank, taxonomic_status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            species.common_name,
            species.scientific_name,
            species.kingdom,
            species.rank,
            species.taxonomic_status
        )
    )

    return {
        "status": "inserted",
        "scientific_name": species.scientific_name
    }