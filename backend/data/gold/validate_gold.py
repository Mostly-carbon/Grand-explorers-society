# Validates Gold trait definitions, observations, and AnimalObservations provenance.

import csv
import sys


csv.field_size_limit(sys.maxsize)


TRAIT_FILE = "data/gold/trait.tsv"
OBSERVATION_FILE = "data/gold/trait_observation.tsv"
RESOLUTION_FILE = (
    "data/gold/animal_observation_species_resolution.tsv"
)
SPECIES_FILE = "data/gold/species.tsv"
SOURCE_FILE = "data/gold/source.tsv"


def load_ids(file_path, field_name):
    ids = set()

    with open(
        file_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            ids.add(row[field_name])

    return ids


def main():
    print("Loading Gold IDs...")

    species_ids = load_ids(
        SPECIES_FILE,
        "id",
    )

    trait_ids = load_ids(
        TRAIT_FILE,
        "id",
    )

    source_ids = load_ids(
        SOURCE_FILE,
        "id",
    )

    print(
        f"Species IDs: {len(species_ids):,}"
    )
    print(
        f"Trait IDs: {len(trait_ids):,}"
    )
    print(
        f"Source IDs: {len(source_ids):,}"
    )

    # Trait definitions
    trait_duplicates = set()
    seen_traits = set()
    trait_missing = 0

    with open(
        TRAIT_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            trait_id = row["id"]

            if trait_id in seen_traits:
                trait_duplicates.add(trait_id)

            seen_traits.add(trait_id)

            for field in [
                "id",
                "name",
                "category",
                "description",
            ]:
                if not row[field].strip():
                    trait_missing += 1

    print()
    print("TRAIT DEFINITIONS")
    print("-----------------")
    print(
        f"Records: {len(trait_ids):,}"
    )
    print(
        f"Duplicate IDs: "
        f"{len(trait_duplicates):,}"
    )
    print(
        f"Missing required fields: "
        f"{trait_missing:,}"
    )

    # Trait observations
    total = 0
    duplicate_ids = set()
    seen_ids = set()

    unresolved_species = 0
    unresolved_traits = 0
    unresolved_sources = 0

    missing_values = 0
    invalid_numeric_values = 0

    with open(
        OBSERVATION_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            total += 1

            observation_id = row["id"]

            if observation_id in seen_ids:
                duplicate_ids.add(
                    observation_id
                )

            seen_ids.add(observation_id)

            if row["species_id"] not in species_ids:
                unresolved_species += 1

            if row["trait_id"] not in trait_ids:
                unresolved_traits += 1

            if row["source_id"] not in source_ids:
                unresolved_sources += 1

            value = row["value_numeric"].strip()

            if not value:
                missing_values += 1
            else:
                try:
                    float(value)
                except ValueError:
                    invalid_numeric_values += 1

    print()
    print("TRAIT OBSERVATIONS")
    print("------------------")
    print(
        f"Records: {total:,}"
    )
    print(
        f"Duplicate IDs: "
        f"{len(duplicate_ids):,}"
    )
    print(
        f"Unresolved species: "
        f"{unresolved_species:,}"
    )
    print(
        f"Unresolved traits: "
        f"{unresolved_traits:,}"
    )
    print(
        f"Unresolved sources: "
        f"{unresolved_sources:,}"
    )
    print(
        f"Missing numeric values: "
        f"{missing_values:,}"
    )
    print(
        f"Invalid numeric values: "
        f"{invalid_numeric_values:,}"
    )

    # Resolution coverage
    resolution_total = 0
    resolved = 0
    unresolved = 0

    with open(
        RESOLUTION_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            resolution_total += 1

            if row["resolved_species_id"].strip():
                resolved += 1
            else:
                unresolved += 1

    print()
    print("RESOLUTION COVERAGE")
    print("-------------------")
    print(
        f"Resolution records: "
        f"{resolution_total:,}"
    )
    print(
        f"Resolved: {resolved:,}"
    )
    print(
        f"Unresolved: {unresolved:,}"
    )

    print()
    print(
        "AnimalObservations Gold validation complete."
    )


if __name__ == "__main__":
    main()