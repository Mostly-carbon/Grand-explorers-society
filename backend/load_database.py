# Loads validated Gold TSV datasets into the production SQLite database.

import csv
import sqlite3
from pathlib import Path


csv.field_size_limit(10_000_000)


DATABASE_PATH = Path("grand_explorers_society.db")
GOLD_DIR = Path("data/gold")

BATCH_SIZE = 10_000


def read_tsv(filename):
    with open(
        GOLD_DIR / filename,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            yield row


def clean(value):
    if value == "":
        return None

    return value


def to_int(value):
    if value in ("", None):
        return None

    return int(value)


def to_float(value):
    if value in ("", None):
        return None

    return float(value)


def to_bool(value):
    if value in ("", None):
        return None

    return 1 if value.lower() == "true" else 0


def insert_batch(connection, sql, rows):
    connection.executemany(sql, rows)
    connection.commit()


def load_source(connection):
    print("Loading source...")

    reader = read_tsv("source.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO source (
            id,
            name,
            url,
            source_type,
            accessed_at
        )
        VALUES (?, ?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            row["name"],
            row["url"],
            row["source_type"],
            clean(row["accessed_at"])
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} sources")


def load_taxon(connection):
    print("Loading taxon...")

    reader = read_tsv("taxon.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO taxon (
            id,
            source_taxon_id,
            scientific_name,
            scientific_name_authorship,
            taxonomic_status,
            rank,
            parent_taxon_id,
            accepted_taxon_id,
            kingdom,
            phylum,
            class,
            "order",
            family,
            genus,
            specific_epithet,
            infraspecific_epithet,
            taxon_remarks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            row["source_taxon_id"],
            row["scientific_name"],
            clean(row["scientific_name_authorship"]),
            row["taxonomic_status"],
            row["rank"],
            to_int(row["parent_taxon_id"]),
            to_int(row["accepted_taxon_id"]),
            clean(row["kingdom"]),
            clean(row["phylum"]),
            clean(row["class"]),
            clean(row["order"]),
            clean(row["family"]),
            clean(row["genus"]),
            clean(row["specific_epithet"]),
            clean(row["infraspecific_epithet"]),
            clean(row["taxon_remarks"])
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

            if count % 500_000 == 0:
                print(f"  Loaded {count:,} taxa")

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} taxa")


def load_species(connection):
    print("Loading species...")

    reader = read_tsv("species.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO species (
            id,
            taxon_id,
            description,
            diet,
            lifespan,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            int(row["taxon_id"]),
            clean(row["description"]),
            clean(row["diet"]),
            clean(row["lifespan"]),
            row["status"]
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} species")


def load_vernacular_names(connection):
    print("Loading vernacular names...")

    reader = read_tsv("vernacular_name.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO vernacular_name (
            id,
            taxon_id,
            language,
            name,
            merged
        )
        VALUES (?, ?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            int(row["taxon_id"]),
            clean(row["language"]),
            row["name"],
            to_bool(row["merged"])
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} vernacular names")


def load_traits(connection):
    print("Loading traits...")

    reader = read_tsv("trait.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO trait (
            id,
            name,
            category,
            description
        )
        VALUES (?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            row["name"],
            row["category"],
            clean(row["description"])
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} traits")


def load_trait_observations(connection):
    print("Loading trait observations...")

    reader = read_tsv("trait_observation.tsv")
    batch = []
    count = 0

    sql = """
        INSERT INTO trait_observation (
            id,
            species_id,
            trait_id,
            value_numeric,
            value_text,
            unit,
            context,
            sample_size,
            source_id,
            source_record_id,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for row in reader:
        batch.append((
            int(row["id"]),
            int(row["species_id"]),
            int(row["trait_id"]),
            to_float(row["value_numeric"]),
            clean(row["value_text"]),
            clean(row["unit"]),
            clean(row["context"]),
            to_int(row["sample_size"]),
            int(row["source_id"]),
            clean(row["source_record_id"]),
            clean(row["notes"])
        ))

        if len(batch) >= BATCH_SIZE:
            insert_batch(connection, sql, batch)
            count += len(batch)
            batch.clear()

            if count % 50_000 == 0:
                print(f"  Loaded {count:,} observations")

    if batch:
        insert_batch(connection, sql, batch)
        count += len(batch)

    print(f"  Loaded {count:,} trait observations")


def main():
    print("Connecting to database...")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")

        load_source(connection)

        # Taxon contains self-referencing parent and accepted relationships.
        # Gold validation has already confirmed these references are valid.
        connection.execute("PRAGMA foreign_keys = OFF")

        load_taxon(connection)

        connection.execute("PRAGMA foreign_keys = ON")

        load_species(connection)
        load_vernacular_names(connection)
        load_traits(connection)
        load_trait_observations(connection)

        connection.commit()

    finally:
        connection.close()

    print()
    print("DATABASE LOAD COMPLETE")


if __name__ == "__main__":
    main()