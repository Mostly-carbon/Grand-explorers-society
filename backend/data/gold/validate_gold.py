# Validates relationships and record integrity in Gold datasets.

import csv
import sys


csv.field_size_limit(sys.maxsize)


TAXON_FILE = "data/gold/taxon.tsv"
SPECIES_FILE = "data/gold/species.tsv"
VERNACULAR_FILE = "data/gold/vernacular_name.tsv"


def load_taxon_ids():
    taxon_ids = set()
    source_taxon_ids = set()

    with open(
        TAXON_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            taxon_ids.add(row["id"])
            source_taxon_ids.add(row["source_taxon_id"])

    return taxon_ids, source_taxon_ids


def validate_taxon_relationships(taxon_ids):
    unresolved_parent = []
    unresolved_accepted = []

    total = 0

    with open(
        TAXON_FILE,
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

            parent_id = row["parent_taxon_id"]

            if parent_id and parent_id not in taxon_ids:
                unresolved_parent.append(
                    (
                        row["id"],
                        row["source_taxon_id"],
                        parent_id,
                        row["scientific_name"],
                    )
                )

            accepted_id = row["accepted_taxon_id"]

            if accepted_id and accepted_id not in taxon_ids:
                unresolved_accepted.append(
                    (
                        row["id"],
                        row["source_taxon_id"],
                        accepted_id,
                        row["scientific_name"],
                    )
                )

    print()
    print("TAXON RELATIONSHIPS")
    print("-------------------")
    print(f"Taxon records: {total:,}")
    print(
        f"Unresolved parent references: "
        f"{len(unresolved_parent):,}"
    )
    print(
        f"Unresolved accepted references: "
        f"{len(unresolved_accepted):,}"
    )

    print()
    print("Sample unresolved parents:")

    for row in unresolved_parent[:10]:
        print(row)

    print()
    print("Sample unresolved accepted references:")

    for row in unresolved_accepted[:10]:
        print(row)

    return unresolved_parent, unresolved_accepted


def validate_species(taxon_ids):
    total = 0
    unresolved = []

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
            total += 1

            if row["taxon_id"] not in taxon_ids:
                unresolved.append(row)

    print()
    print("SPECIES")
    print("-------")
    print(f"Species records: {total:,}")
    print(
        f"Unresolved taxon references: "
        f"{len(unresolved):,}"
    )

    return unresolved


def validate_vernacular_names(taxon_ids):
    total = 0
    unresolved = []

    with open(
        VERNACULAR_FILE,
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

            if row["taxon_id"] not in taxon_ids:
                unresolved.append(row)

    print()
    print("VERNACULAR NAMES")
    print("----------------")
    print(f"Vernacular records: {total:,}")
    print(
        f"Unresolved taxon references: "
        f"{len(unresolved):,}"
    )

    print()
    print("Sample unresolved vernacular names:")

    for row in unresolved[:10]:
        print(row)

    return unresolved


def main():
    print("Loading Gold taxon IDs...")

    taxon_ids, source_taxon_ids = load_taxon_ids()

    print(
        f"Gold internal taxon IDs: "
        f"{len(taxon_ids):,}"
    )

    print(
        f"Gold source taxon IDs: "
        f"{len(source_taxon_ids):,}"
    )

    validate_taxon_relationships(
        taxon_ids,
    )

    validate_species(
        taxon_ids,
    )

    validate_vernacular_names(
        taxon_ids,
    )


if __name__ == "__main__":
    main()