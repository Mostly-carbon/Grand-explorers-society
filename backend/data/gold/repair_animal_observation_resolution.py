# Repairs AnimalObservations resolution species IDs using Gold taxon-to-species relationships.

import csv
import os
import sys


csv.field_size_limit(sys.maxsize)


RESOLUTION_FILE = (
    "data/gold/animal_observation_species_resolution.tsv"
)

SPECIES_FILE = (
    "data/gold/species.tsv"
)

TEMP_FILE = (
    "data/gold/"
    "animal_observation_species_resolution.tmp.tsv"
)


def clean_text(value):
    if value is None:
        return ""

    return value.strip()


def load_taxon_to_species():
    mapping = {}

    with open(
        SPECIES_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            taxon_id = clean_text(
                row["taxon_id"]
            )

            species_id = clean_text(
                row["id"]
            )

            if taxon_id:
                mapping[taxon_id] = species_id

    return mapping


def main():
    print("Loading Gold taxon-to-species mapping...")

    taxon_to_species = (
        load_taxon_to_species()
    )

    print(
        "Taxon-to-species mappings: "
        f"{len(taxon_to_species):,}"
    )

    repaired = 0
    already_valid = 0
    unresolved = 0
    missing_mapping = 0

    with open(
        RESOLUTION_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as source_file, open(
        TEMP_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:

        reader = csv.DictReader(
            source_file,
            delimiter="\t",
        )

        fieldnames = reader.fieldnames

        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for row in reader:
            status = clean_text(
                row["resolution_status"]
            )

            if status != "resolved":
                unresolved += 1
                writer.writerow(row)
                continue

            taxon_id = clean_text(
                row["resolved_taxon_id"]
            )

            species_id = taxon_to_species.get(
                taxon_id
            )

            if species_id:
                old_species_id = clean_text(
                    row["resolved_species_id"]
                )

                if old_species_id == species_id:
                    already_valid += 1
                else:
                    row["resolved_species_id"] = (
                        species_id
                    )
                    repaired += 1
            else:
                row["resolved_species_id"] = ""
                row["resolution_status"] = (
                    "unresolved"
                )
                missing_mapping += 1

            writer.writerow(row)

    os.replace(
        TEMP_FILE,
        RESOLUTION_FILE,
    )

    print()
    print("RESOLUTION REPAIR")
    print("-----------------")
    print(
        f"Repaired: {repaired:,}"
    )
    print(
        f"Already valid: {already_valid:,}"
    )
    print(
        f"Unresolved: {unresolved:,}"
    )
    print(
        f"Missing taxon-to-species mapping: "
        f"{missing_mapping:,}"
    )

    print()
    print(
        "Resolution repair complete."
    )


if __name__ == "__main__":
    main()