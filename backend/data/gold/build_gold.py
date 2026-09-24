# Builds Gold datasets from validated Silver datasets.

import csv
import os
import sqlite3
import sys


csv.field_size_limit(sys.maxsize)


GOLD_TAXON_FIELDS = [
    "id",
    "source_taxon_id",
    "scientific_name",
    "scientific_name_authorship",
    "taxonomic_status",
    "rank",
    "parent_taxon_id",
    "accepted_taxon_id",
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "specific_epithet",
    "infraspecific_epithet",
    "taxon_remarks",
]


GOLD_SPECIES_FIELDS = [
    "id",
    "taxon_id",
    "description",
    "diet",
    "lifespan",
    "status",
]


GOLD_VERNACULAR_FIELDS = [
    "id",
    "taxon_id",
    "language",
    "name",
    "merged",
]


GOLD_SOURCE_FIELDS = [
    "id",
    "name",
    "url",
    "source_type",
    "accessed_at",
]


TAXON_MAP_DB = "data/gold/taxon_id_map.db"


def create_taxon_id_map(input_path):
    print("Creating temporary taxon ID map...", flush=True)

    if os.path.exists(TAXON_MAP_DB):
        os.remove(TAXON_MAP_DB)

    connection = sqlite3.connect(TAXON_MAP_DB)

    try:
        connection.execute(
            """
            CREATE TABLE taxon_id_map (
                source_taxon_id TEXT PRIMARY KEY,
                gold_taxon_id INTEGER NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX idx_taxon_id_map_source
            ON taxon_id_map(source_taxon_id)
            """
        )

        with open(
            input_path,
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file:

            reader = csv.DictReader(
                input_file,
                delimiter="\t",
            )

            batch = []
            taxon_count = 0

            for gold_id, record in enumerate(reader, 1):
                source_taxon_id = record["taxon_id"]

                batch.append(
                    (
                        source_taxon_id,
                        gold_id,
                    )
                )

                taxon_count += 1

                if len(batch) >= 10000:
                    connection.executemany(
                        """
                        INSERT INTO taxon_id_map (
                            source_taxon_id,
                            gold_taxon_id
                        )
                        VALUES (?, ?)
                        """,
                        batch,
                    )

                    connection.commit()
                    batch.clear()

                if taxon_count % 500000 == 0:
                    print(
                        f"Mapped {taxon_count:,} taxon IDs...",
                        flush=True,
                    )

            if batch:
                connection.executemany(
                    """
                    INSERT INTO taxon_id_map (
                        source_taxon_id,
                        gold_taxon_id
                    )
                    VALUES (?, ?)
                    """,
                    batch,
                )

                connection.commit()

        print(
            f"Taxon ID map complete: {taxon_count:,} records.",
            flush=True,
        )

    finally:
        connection.close()


def lookup_gold_taxon_id(connection, source_taxon_id):
    if not source_taxon_id:
        return ""

    result = connection.execute(
        """
        SELECT gold_taxon_id
        FROM taxon_id_map
        WHERE source_taxon_id = ?
        """,
        (source_taxon_id,),
    ).fetchone()

    if result is None:
        return ""

    return result[0]


def build_taxon_gold(input_path, output_path):
    print("Building Gold taxon dataset...", flush=True)

    connection = sqlite3.connect(TAXON_MAP_DB)

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file, open(
            output_path,
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:

            reader = csv.DictReader(
                input_file,
                delimiter="\t",
            )

            writer = csv.DictWriter(
                output_file,
                fieldnames=GOLD_TAXON_FIELDS,
                delimiter="\t",
            )

            writer.writeheader()

            unresolved_parent = 0
            unresolved_accepted = 0
            taxon_count = 0

            for gold_id, record in enumerate(reader, 1):

                parent_taxon_id = lookup_gold_taxon_id(
                    connection,
                    record["parent_taxon_id"],
                )

                accepted_taxon_id = lookup_gold_taxon_id(
                    connection,
                    record["accepted_taxon_id"],
                )

                if (
                    record["parent_taxon_id"]
                    and not parent_taxon_id
                ):
                    unresolved_parent += 1

                if (
                    record["accepted_taxon_id"]
                    and not accepted_taxon_id
                ):
                    unresolved_accepted += 1

                writer.writerow(
                    {
                        "id": gold_id,
                        "source_taxon_id": record["taxon_id"],
                        "scientific_name": record[
                            "scientific_name"
                        ],
                        "scientific_name_authorship": record[
                            "scientific_name_authorship"
                        ],
                        "taxonomic_status": record[
                            "taxonomic_status"
                        ],
                        "rank": record["taxon_rank"],
                        "parent_taxon_id": parent_taxon_id,
                        "accepted_taxon_id": accepted_taxon_id,
                        "kingdom": record["kingdom"],
                        "phylum": record["phylum"],
                        "class": record["class_name"],
                        "order": record["order"],
                        "family": record["family"],
                        "genus": record["genus"],
                        "specific_epithet": record[
                            "specific_epithet"
                        ],
                        "infraspecific_epithet": record[
                            "infraspecific_epithet"
                        ],
                        "taxon_remarks": record[
                            "taxon_remarks"
                        ],
                    }
                )

                taxon_count += 1

                if taxon_count % 500000 == 0:
                    print(
                        f"Built {taxon_count:,} Gold taxon records...",
                        flush=True,
                    )

        print(
            f"Gold taxon complete: {taxon_count:,} records.",
            flush=True,
        )

        print(
            f"Unresolved parent references: "
            f"{unresolved_parent:,}",
            flush=True,
        )

        print(
            f"Unresolved accepted references: "
            f"{unresolved_accepted:,}",
            flush=True,
        )

    finally:
        connection.close()


def build_species_gold(input_path, output_path):
    print("Building Gold species dataset...", flush=True)

    with open(
        input_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as input_file, open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:

        reader = csv.DictReader(
            input_file,
            delimiter="\t",
        )

        writer = csv.DictWriter(
            output_file,
            fieldnames=GOLD_SPECIES_FIELDS,
            delimiter="\t",
        )

        writer.writeheader()

        species_id = 0

        for record in reader:

            if (
                record["rank"] == "species"
                and record["taxonomic_status"]
                in {
                    "accepted",
                    "provisionally accepted",
                }
            ):
                species_id += 1

                writer.writerow(
                    {
                        "id": species_id,
                        "taxon_id": record["id"],
                        "description": "",
                        "diet": "",
                        "lifespan": "",
                        "status": "valid",
                    }
                )

                if species_id % 500000 == 0:
                    print(
                        f"Built {species_id:,} Gold species records...",
                        flush=True,
                    )

    print(
        f"Gold species complete: {species_id:,} records.",
        flush=True,
    )


def build_vernacular_gold(input_path, output_path):
    print(
        "Building Gold vernacular-name dataset...",
        flush=True,
    )

    connection = sqlite3.connect(TAXON_MAP_DB)

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8",
            newline="",
        ) as input_file, open(
            output_path,
            "w",
            encoding="utf-8",
            newline="",
        ) as output_file:

            reader = csv.DictReader(
                input_file,
                delimiter="\t",
            )

            writer = csv.DictWriter(
                output_file,
                fieldnames=GOLD_VERNACULAR_FIELDS,
                delimiter="\t",
            )

            writer.writeheader()

            name_id = 0
            unresolved_taxa = 0

            for record in reader:

                gold_taxon_id = lookup_gold_taxon_id(
                    connection,
                    record["taxon_id"],
                )

                if not gold_taxon_id:
                    unresolved_taxa += 1
                    continue

                name_id += 1

                writer.writerow(
                    {
                        "id": name_id,
                        "taxon_id": gold_taxon_id,
                        "language": record["language"],
                        "name": record["vernacular_name"],
                        "merged": record["merged"],
                    }
                )

                if name_id % 500000 == 0:
                    print(
                        f"Built {name_id:,} Gold "
                        f"vernacular-name records...",
                        flush=True,
                    )

        print(
            f"Gold vernacular names complete: "
            f"{name_id:,} records.",
            flush=True,
        )

        print(
            f"Unresolved vernacular taxon references: "
            f"{unresolved_taxa:,}",
            flush=True,
        )

    finally:
        connection.close()


def build_source_gold(output_path):
    print("Building Gold source dataset...", flush=True)

    sources = [
        {
            "id": 1,
            "name": "Catalogue of Life",
            "url": "https://www.catalogueoflife.org/",
            "source_type": "taxonomy",
            "accessed_at": "",
        },
        {
            "id": 2,
            "name": "AnimalTraits",
            "url": "https://animaltraits.org/",
            "source_type": "animal_traits",
            "accessed_at": "",
        },
        {
            "id": 3,
            "name": "EltonTraits 1.0",
            "url": (
                "https://doi.org/"
                "10.6084/m9.figshare.c.3306933.v1"
            ),
            "source_type": "animal_traits",
            "accessed_at": "",
        },
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:

        writer = csv.DictWriter(
            output_file,
            fieldnames=GOLD_SOURCE_FIELDS,
            delimiter="\t",
        )

        writer.writeheader()

        for source in sources:
            writer.writerow(source)

    print(
        f"Gold source complete: {len(sources)} records.",
        flush=True,
    )


def cleanup_taxon_id_map():
    if os.path.exists(TAXON_MAP_DB):
        os.remove(TAXON_MAP_DB)

        print(
            "Temporary taxon ID map removed.",
            flush=True,
        )


if __name__ == "__main__":

    silver_taxon = "data/silver/taxon.tsv"
    silver_vernacular = "data/silver/vernacular_name.tsv"

    gold_taxon = "data/gold/taxon.tsv"
    gold_species = "data/gold/species.tsv"
    gold_vernacular = "data/gold/vernacular_name.tsv"
    gold_source = "data/gold/source.tsv"

    try:
        create_taxon_id_map(
            silver_taxon,
        )

        build_taxon_gold(
            silver_taxon,
            gold_taxon,
        )

        build_species_gold(
            gold_taxon,
            gold_species,
        )

        build_vernacular_gold(
            silver_vernacular,
            gold_vernacular,
        )

        build_source_gold(
            gold_source,
        )

    finally:
        cleanup_taxon_id_map()

    print()
    print("Gold build complete.")