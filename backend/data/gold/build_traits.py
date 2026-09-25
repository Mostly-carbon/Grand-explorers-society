# Builds Gold trait definitions and AnimalObservations trait records.

import csv
import os
import sys


csv.field_size_limit(sys.maxsize)


SILVER_FILE = (
    "data/silver/animal_observations.tsv"
)

RESOLUTION_FILE = (
    "data/gold/animal_observation_species_resolution.tsv"
)

SOURCE_FILE = (
    "data/gold/source.tsv"
)

TRAIT_FILE = (
    "data/gold/trait.tsv"
)

TRAIT_OBSERVATION_FILE = (
    "data/gold/trait_observation.tsv"
)


TRAITS = {
    "body_mass": {
        "name": "Body mass",
        "category": "physical",
        "description": (
            "Mass of the organism."
        ),
    },
    "metabolic_rate": {
        "name": "Metabolic rate",
        "category": "physiology",
        "description": (
            "Rate of energy expenditure "
            "or metabolism."
        ),
    },
    "mass_specific_metabolic_rate": {
        "name": "Mass-specific metabolic rate",
        "category": "physiology",
        "description": (
            "Metabolic rate normalized "
            "by body mass."
        ),
    },
    "brain_size": {
        "name": "Brain size",
        "category": "physical",
        "description": (
            "Measured brain size."
        ),
    },
}


def clean_text(value):
    if value is None:
        return ""

    return value.strip()


def to_optional_float(value):
    value = clean_text(value)

    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def load_sources():
    sources = {}

    with open(
        SOURCE_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            sources[
                clean_text(row["name"])
            ] = row["id"]

    return sources


def load_resolution():
    resolutions = []

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

        for row_number, row in enumerate(
            reader,
            start=1,
        ):
            row["_row_number"] = row_number
            resolutions.append(row)

    return resolutions


def rewrite_resolution_with_row_ids(
    resolutions,
):
    fieldnames = [
        "source_row_id",
        "source_name",
        "resolved_taxon_id",
        "resolved_species_id",
        "resolution_type",
        "resolution_status",
    ]

    with open(
        RESOLUTION_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for row in resolutions:
            writer.writerow(
                {
                    "source_row_id": row[
                        "_row_number"
                    ],
                    "source_name": row[
                        "source_name"
                    ],
                    "resolved_taxon_id": row[
                        "resolved_taxon_id"
                    ],
                    "resolved_species_id": row[
                        "resolved_species_id"
                    ],
                    "resolution_type": row[
                        "resolution_type"
                    ],
                    "resolution_status": row[
                        "resolution_status"
                    ],
                }
            )


def build_trait_table():
    fieldnames = [
        "id",
        "name",
        "category",
        "description",
    ]

    trait_ids = {}

    with open(
        TRAIT_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for trait_id, trait in TRAITS.items():
            internal_id = str(
                len(trait_ids) + 1
            )

            trait_ids[trait_id] = internal_id

            writer.writerow(
                {
                    "id": internal_id,
                    "name": trait["name"],
                    "category": trait["category"],
                    "description": trait[
                        "description"
                    ],
                }
            )

    return trait_ids


def make_observation(
    observation_id,
    source_row_id,
    species_id,
    trait_id,
    value,
    minimum,
    maximum,
    unit,
    context,
    sample_size,
    source_id,
    notes,
):
    return {
        "id": str(observation_id),
        "species_id": species_id,
        "trait_id": trait_id,
        "value_numeric": value,
        "value_minimum": minimum,
        "value_maximum": maximum,
        "unit": unit,
        "context": context,
        "sample_size": sample_size,
        "source_id": source_id,
        "source_record_id": (
            f"animal_observations:"
            f"{source_row_id}"
        ),
        "notes": notes,
    }


def build_trait_observations(
    resolutions,
    trait_ids,
    sources,
):
    observations = []

    with open(
        SILVER_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row_number, row in enumerate(
            reader,
            start=1,
        ):
            resolution = resolutions[
                row_number - 1
            ]

            species_id = clean_text(
                resolution[
                    "resolved_species_id"
                ]
            )

            if not species_id:
                continue

            source_id = sources.get(
                "AnimalTraits"
            )

            if not source_id:
                raise ValueError(
                    "Could not find "
                    "AnimalTraits in source.tsv."
                )

            sample_size = clean_text(
                row["sample_size"]
            )

            scientific_name = clean_text(
                row["species"]
            )

            # Body mass
            body_mass = to_optional_float(
                row["body_mass"]
            )

            if body_mass is not None:
                observations.append(
                    make_observation(
                        len(observations) + 1,
                        row_number,
                        species_id,
                        trait_ids[
                            "body_mass"
                        ],
                        body_mass,
                        to_optional_float(
                            row[
                                "body_mass_minimum"
                            ]
                        ),
                        to_optional_float(
                            row[
                                "body_mass_maximum"
                            ]
                        ),
                        clean_text(
                            row[
                                "body_mass_units"
                            ]
                        ),
                        clean_text(
                            row[
                                "body_mass_method"
                            ]
                        ),
                        sample_size,
                        source_id,
                        clean_text(
                            row[
                                "body_mass_comments"
                            ]
                        ),
                    )
                )

            # Metabolic rate
            metabolic_rate = (
                to_optional_float(
                    row["metabolic_rate"]
                )
            )

            if metabolic_rate is not None:
                observations.append(
                    make_observation(
                        len(observations) + 1,
                        row_number,
                        species_id,
                        trait_ids[
                            "metabolic_rate"
                        ],
                        metabolic_rate,
                        to_optional_float(
                            row[
                                "metabolic_rate_minimum"
                            ]
                        ),
                        to_optional_float(
                            row[
                                "metabolic_rate_maximum"
                            ]
                        ),
                        clean_text(
                            row[
                                "metabolic_rate_units"
                            ]
                        ),
                        clean_text(
                            row[
                                "metabolic_rate_method"
                            ]
                        ),
                        sample_size,
                        source_id,
                        clean_text(
                            row[
                                "metabolic_rate_comments"
                            ]
                        ),
                    )
                )

            # Mass-specific metabolic rate
            mass_specific = (
                to_optional_float(
                    row[
                        "mass_specific_metabolic_rate"
                    ]
                )
            )

            if mass_specific is not None:
                observations.append(
                    make_observation(
                        len(observations) + 1,
                        row_number,
                        species_id,
                        trait_ids[
                            "mass_specific_metabolic_rate"
                        ],
                        mass_specific,
                        None,
                        None,
                        clean_text(
                            row[
                                "mass_specific_metabolic_rate_units"
                            ]
                        ),
                        "",
                        sample_size,
                        source_id,
                        "",
                    )
                )

            # Brain size
            brain_size = to_optional_float(
                row["brain_size"]
            )

            if brain_size is not None:
                observations.append(
                    make_observation(
                        len(observations) + 1,
                        row_number,
                        species_id,
                        trait_ids[
                            "brain_size"
                        ],
                        brain_size,
                        to_optional_float(
                            row[
                                "brain_size_minimum"
                            ]
                        ),
                        to_optional_float(
                            row[
                                "brain_size_maximum"
                            ]
                        ),
                        clean_text(
                            row[
                                "brain_size_units"
                            ]
                        ),
                        clean_text(
                            row[
                                "brain_size_method"
                            ]
                        ),
                        sample_size,
                        source_id,
                        clean_text(
                            row[
                                "brain_size_comments"
                            ]
                        ),
                    )
                )

    return observations


def write_observations(observations):
    fieldnames = [
        "id",
        "species_id",
        "trait_id",
        "value_numeric",
        "value_minimum",
        "value_maximum",
        "unit",
        "context",
        "sample_size",
        "source_id",
        "source_record_id",
        "notes",
    ]

    with open(
        TRAIT_OBSERVATION_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        writer.writerows(observations)


def main():
    print(
        "Loading existing resolution..."
    )

    resolutions = load_resolution()

    print(
        f"Resolution records: "
        f"{len(resolutions):,}"
    )

    print(
        "Adding source row IDs..."
    )

    rewrite_resolution_with_row_ids(
        resolutions
    )

    print(
        "Loading Gold sources..."
    )

    sources = load_sources()

    print(
        "Building trait definitions..."
    )

    trait_ids = build_trait_table()

    print(
        f"Trait definitions: "
        f"{len(trait_ids):,}"
    )

    print(
        "Building trait observations..."
    )

    observations = (
        build_trait_observations(
            resolutions,
            trait_ids,
            sources,
        )
    )

    write_observations(
        observations
    )

    resolved = sum(
        1
        for row in resolutions
        if clean_text(
            row["resolved_species_id"]
        )
    )

    unresolved = (
        len(resolutions) - resolved
    )

    print()
    print(
        "ANIMALOBSERVATIONS GOLD BUILD"
    )
    print(
        "-----------------------------"
    )
    print(
        f"Input rows: {len(resolutions):,}"
    )
    print(
        f"Resolved rows: {resolved:,}"
    )
    print(
        f"Unresolved rows: {unresolved:,}"
    )
    print(
        f"Trait definitions: "
        f"{len(trait_ids):,}"
    )
    print(
        f"Trait observations: "
        f"{len(observations):,}"
    )

    print()
    print(
        "Created:"
    )
    print(TRAIT_FILE)
    print(TRAIT_OBSERVATION_FILE)
    print(RESOLUTION_FILE)

    print()
    print(
        "AnimalObservations Gold build complete."
    )


if __name__ == "__main__":
    main()