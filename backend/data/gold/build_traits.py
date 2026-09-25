# Builds Gold trait definitions and trait observations from Silver trait datasets.

import csv
import sys


csv.field_size_limit(sys.maxsize)


SILVER_ANIMAL_FILE = "data/silver/animal_observations.tsv"
SILVER_BIRD_FILE = "data/silver/elton_birds.tsv"
SILVER_MAMMAL_FILE = "data/silver/elton_mammals.tsv"

RESOLUTION_FILE = (
    "data/gold/animal_observation_species_resolution.tsv"
)

TAXON_FILE = "data/gold/taxon.tsv"
SPECIES_FILE = "data/gold/species.tsv"
SOURCE_FILE = "data/gold/source.tsv"

TRAIT_FILE = "data/gold/trait.tsv"
TRAIT_OBSERVATION_FILE = "data/gold/trait_observation.tsv"


BASE_TRAITS = {
    "body_mass": (
        "Body mass",
        "physical",
        "Mass of the organism.",
    ),
    "metabolic_rate": (
        "Metabolic rate",
        "physiology",
        "Rate of energy expenditure or metabolism.",
    ),
    "mass_specific_metabolic_rate": (
        "Mass-specific metabolic rate",
        "physiology",
        "Metabolic rate normalized by body mass.",
    ),
    "brain_size": (
        "Brain size",
        "physical",
        "Measured brain size.",
    ),
}


ELTON_TRAITS = {
    "diet_inv": (
        "Diet: invertebrates",
        "diet",
        "Percentage of diet consisting of invertebrates.",
    ),
    "diet_vend": (
        "Diet: vertebrate endotherms",
        "diet",
        "Percentage of diet consisting of vertebrate endotherms.",
    ),
    "diet_vect": (
        "Diet: vertebrate ectotherms",
        "diet",
        "Percentage of diet consisting of vertebrate ectotherms.",
    ),
    "diet_vfish": (
        "Diet: vertebrate fish",
        "diet",
        "Percentage of diet consisting of fish.",
    ),
    "diet_vunk": (
        "Diet: vertebrates, unknown",
        "diet",
        "Percentage of diet consisting of vertebrates of unknown type.",
    ),
    "diet_scav": (
        "Diet: scavenged material",
        "diet",
        "Percentage of diet obtained through scavenging.",
    ),
    "diet_fruit": (
        "Diet: fruit",
        "diet",
        "Percentage of diet consisting of fruit.",
    ),
    "diet_nect": (
        "Diet: nectar",
        "diet",
        "Percentage of diet consisting of nectar.",
    ),
    "diet_seed": (
        "Diet: seeds",
        "diet",
        "Percentage of diet consisting of seeds.",
    ),
    "diet_planto": (
        "Diet: plant material",
        "diet",
        "Percentage of diet consisting of plant material.",
    ),
    "for_strat_watbelowsurf": (
        "Foraging: below water surface",
        "foraging",
        "Percentage associated with foraging below the water surface.",
    ),
    "for_strat_wataroundsurf": (
        "Foraging: around water surface",
        "foraging",
        "Percentage associated with foraging around the water surface.",
    ),
    "for_strat_ground": (
        "Foraging: ground",
        "foraging",
        "Percentage associated with ground foraging.",
    ),
    "for_strat_understory": (
        "Foraging: understory",
        "foraging",
        "Percentage associated with understory foraging.",
    ),
    "for_strat_midhigh": (
        "Foraging: mid/high vegetation",
        "foraging",
        "Percentage associated with mid/high vegetation foraging.",
    ),
    "for_strat_canopy": (
        "Foraging: canopy",
        "foraging",
        "Percentage associated with canopy foraging.",
    ),
    "for_strat_aerial": (
        "Foraging: aerial",
        "foraging",
        "Percentage associated with aerial foraging.",
    ),
    "for_strat_value": (
        "Foraging strategy",
        "foraging",
        "Foraging strategy value recorded by EltonTraits.",
    ),
    "pelagic_specialist": (
        "Pelagic specialist",
        "foraging",
        "Pelagic specialization value recorded by EltonTraits.",
    ),
    "nocturnal": (
        "Nocturnal activity",
        "activity",
        "Nocturnal activity value recorded by EltonTraits.",
    ),
    "activity_crepuscular": (
        "Crepuscular activity",
        "activity",
        "Crepuscular activity value recorded by EltonTraits.",
    ),
    "activity_diurnal": (
        "Diurnal activity",
        "activity",
        "Diurnal activity value recorded by EltonTraits.",
    ),
}


def clean_text(value):
    if value is None:
        return ""

    return value.strip()


def to_float(value):
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
            name = clean_text(row["name"]).lower()

            sources[name] = row["id"]

    return sources


def find_source_id(sources, name):
    target = name.lower()

    for source_name, source_id in sources.items():
        if target in source_name:
            return source_id

    raise RuntimeError(
        f"Could not find source matching '{name}' in source.tsv."
    )


def load_species_map():
    taxon_to_species = {}

    print("Loading Gold species mapping...")

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

            if taxon_id and species_id:
                taxon_to_species[taxon_id] = species_id

    print(
        f"Gold taxon → species mappings: "
        f"{len(taxon_to_species):,}"
    )

    return taxon_to_species


def load_resolution():
    resolutions = {}

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
            source_row_id = clean_text(
                row["source_row_id"]
            )

            species_id = clean_text(
                row["resolved_species_id"]
            )

            if source_row_id:
                resolutions[source_row_id] = species_id

    return resolutions


def load_elton_name_map(taxon_to_species):
    name_to_species = {}

    print(
        "Scanning Gold taxon for Elton species names "
        "and synonyms..."
    )

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
            taxon_id = clean_text(row["id"])

            rank = clean_text(
                row["rank"]
            ).lower()

            # Elton uses species-level binomial names.
            # Only use species-rank COL records for matching.
            if rank != "species":
                continue

            genus = clean_text(
                row["genus"]
            )

            specific_epithet = clean_text(
                row["specific_epithet"]
            )

            if not genus or not specific_epithet:
                continue

            scientific_name = (
                f"{genus} {specific_epithet}"
            )

            status = clean_text(
                row["taxonomic_status"]
            ).lower()

            species_id = None

            # Accepted/provisionally accepted species.
            if (
                status in {
                    "accepted",
                    "provisionally accepted",
                }
                and taxon_id in taxon_to_species
            ):
                species_id = taxon_to_species[
                    taxon_id
                ]

            # Synonym → accepted species.
            elif status in {
                "synonym",
                "ambiguous synonym",
                "misapplied",
            }:
                accepted_taxon_id = clean_text(
                    row["accepted_taxon_id"]
                )

                if accepted_taxon_id:
                    species_id = taxon_to_species.get(
                        accepted_taxon_id
                    )

            if not species_id:
                continue

            existing = name_to_species.get(
                scientific_name
            )

            if existing is None:
                name_to_species[
                    scientific_name
                ] = species_id

            elif existing != species_id:
                # Same binomial maps to multiple Gold species.
                # Remove it rather than guessing.
                del name_to_species[
                    scientific_name
                ]

    print(
        f"Elton scientific-name mappings: "
        f"{len(name_to_species):,}"
    )

    return name_to_species


def build_trait_table():
    traits = {
        **BASE_TRAITS,
        **ELTON_TRAITS,
    }

    trait_ids = {}

    with open(
        TRAIT_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "name",
                "category",
                "description",
            ],
            delimiter="\t",
        )

        writer.writeheader()

        for index, (key, values) in enumerate(
            traits.items(),
            start=1,
        ):

            name, category, description = values

            trait_ids[key] = str(index)

            writer.writerow(
                {
                    "id": str(index),
                    "name": name,
                    "category": category,
                    "description": description,
                }
            )

    print(
        f"Trait definitions: {len(trait_ids):,}"
    )

    return trait_ids


def write_observation(
    writer,
    observation_id,
    species_id,
    trait_id,
    value,
    unit,
    context,
    sample_size,
    source_id,
    source_record_id,
    notes,
):
    if value is None:
        return observation_id

    observation_id += 1

    writer.writerow(
        {
            "id": str(observation_id),
            "species_id": species_id,
            "trait_id": trait_id,
            "value_numeric": value,
            "value_text": "",
            "unit": unit,
            "context": context,
            "sample_size": sample_size,
            "source_id": source_id,
            "source_record_id": source_record_id,
            "notes": notes,
        }
    )

    return observation_id


def build_animal_observations(
    writer,
    trait_ids,
    source_id,
    resolutions,
    observation_id,
):
    print()
    print("Building AnimalObservations...")

    rows = 0
    written = 0

    with open(
        SILVER_ANIMAL_FILE,
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
            rows += 1

            species_id = resolutions.get(
                str(row_number),
                "",
            )

            if not species_id:
                continue

            source_record_id = (
                f"animal_observations:{row_number}"
            )

            sample_size = clean_text(
                row.get("sample_size")
            )

            for field in [
                "body_mass",
                "metabolic_rate",
                "mass_specific_metabolic_rate",
                "brain_size",
            ]:

                value = to_float(
                    row.get(field)
                )

                if value is None:
                    continue

                unit = clean_text(
                    row.get(
                        f"{field}_units"
                    )
                )

                context = clean_text(
                    row.get(
                        f"{field}_method"
                    )
                )

                notes = clean_text(
                    row.get(
                        f"{field}_comments"
                    )
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[field],
                    value,
                    unit,
                    context,
                    sample_size,
                    source_id,
                    source_record_id,
                    notes,
                )

                written += 1

    print(
        f"Input rows: {rows:,}"
    )
    print(
        f"Trait observations: {written:,}"
    )

    return observation_id


def build_elton_birds(
    writer,
    trait_ids,
    source_id,
    species_map,
    observation_id,
):
    print()
    print("Building EltonTraits birds...")

    rows = 0
    matched = 0
    unmatched = 0
    written = 0

    diet_fields = [
        "diet_inv",
        "diet_vend",
        "diet_vect",
        "diet_vfish",
        "diet_vunk",
        "diet_scav",
        "diet_fruit",
        "diet_nect",
        "diet_seed",
        "diet_planto",
    ]

    foraging_fields = [
        "for_strat_watbelowsurf",
        "for_strat_wataroundsurf",
        "for_strat_ground",
        "for_strat_understory",
        "for_strat_midhigh",
        "for_strat_canopy",
        "for_strat_aerial",
    ]

    with open(
        SILVER_BIRD_FILE,
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
            rows += 1

            scientific_name = clean_text(
                row["scientific"]
            )

            species_id = species_map.get(
                scientific_name
            )

            if not species_id:
                unmatched += 1
                continue

            matched += 1

            source_record_id = (
                f"elton_birds:{row_number}"
            )

            for field in diet_fields:
                value = to_float(
                    row.get(field)
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[field],
                    value,
                    "%",
                    "EltonTraits diet",
                    "",
                    source_id,
                    source_record_id,
                    (
                        f"certainty="
                        f"{clean_text(row.get('diet_certainty'))}; "
                        f"reference="
                        f"{clean_text(row.get('diet_source'))}"
                    ),
                )

                if value is not None:
                    written += 1

            for field in foraging_fields:
                value = to_float(
                    row.get(field)
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[field],
                    value,
                    "%",
                    "EltonTraits foraging",
                    "",
                    source_id,
                    source_record_id,
                    (
                        f"certainty="
                        f"{clean_text(row.get('for_strat_spec_level'))}; "
                        f"reference="
                        f"{clean_text(row.get('for_strat_source'))}"
                    ),
                )

                if value is not None:
                    written += 1

            for field in [
                "pelagic_specialist",
                "nocturnal",
            ]:
                value = to_float(
                    row.get(field)
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[field],
                    value,
                    "",
                    "EltonTraits",
                    "",
                    source_id,
                    source_record_id,
                    "",
                )

                if value is not None:
                    written += 1

            body_mass = to_float(
                row.get("body_mass_value")
            )

            observation_id = write_observation(
                writer,
                observation_id,
                species_id,
                trait_ids["body_mass"],
                body_mass,
                "g",
                "EltonTraits body mass",
                "",
                source_id,
                source_record_id,
                (
                    f"source="
                    f"{clean_text(row.get('body_mass_source'))}; "
                    f"spec_level="
                    f"{clean_text(row.get('body_mass_spec_level'))}; "
                    f"comment="
                    f"{clean_text(row.get('body_mass_comment'))}"
                ),
            )

            if body_mass is not None:
                written += 1

    print(f"Input rows: {rows:,}")
    print(f"Matched: {matched:,}")
    print(f"Unmatched: {unmatched:,}")
    print(f"Trait observations: {written:,}")

    return observation_id


def build_elton_mammals(
    writer,
    trait_ids,
    source_id,
    species_map,
    observation_id,
):
    print()
    print("Building EltonTraits mammals...")

    rows = 0
    matched = 0
    unmatched = 0
    written = 0

    diet_fields = [
        "diet_inv",
        "diet_vend",
        "diet_vect",
        "diet_vfish",
        "diet_vunk",
        "diet_scav",
        "diet_fruit",
        "diet_nect",
        "diet_seed",
        "diet_planto",
    ]

    activity_fields = [
        ("activity_nocturnal", "nocturnal"),
        ("activity_crepuscular", "activity_crepuscular"),
        ("activity_diurnal", "activity_diurnal"),
    ]

    with open(
        SILVER_MAMMAL_FILE,
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
            rows += 1

            scientific_name = clean_text(
                row["scientific"]
            )

            species_id = species_map.get(
                scientific_name
            )

            if not species_id:
                unmatched += 1
                continue

            matched += 1

            source_record_id = (
                f"elton_mammals:{row_number}"
            )

            for field in diet_fields:
                value = to_float(
                    row.get(field)
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[field],
                    value,
                    "%",
                    "EltonTraits diet",
                    "",
                    source_id,
                    source_record_id,
                    (
                        f"certainty="
                        f"{clean_text(row.get('diet_certainty'))}; "
                        f"reference="
                        f"{clean_text(row.get('diet_source'))}"
                    ),
                )

                if value is not None:
                    written += 1

            for source_field, trait_name in activity_fields:
                value = to_float(
                    row.get(source_field)
                )

                observation_id = write_observation(
                    writer,
                    observation_id,
                    species_id,
                    trait_ids[trait_name],
                    value,
                    "",
                    "EltonTraits activity",
                    "",
                    source_id,
                    source_record_id,
                    (
                        f"certainty="
                        f"{clean_text(row.get('activity_certainty'))}; "
                        f"reference="
                        f"{clean_text(row.get('activity_source'))}"
                    ),
                )

                if value is not None:
                    written += 1

            foraging = to_float(
                row.get("for_strat_value")
            )

            observation_id = write_observation(
                writer,
                observation_id,
                species_id,
                trait_ids["for_strat_value"],
                foraging,
                "",
                "EltonTraits foraging",
                "",
                source_id,
                source_record_id,
                (
                    f"certainty="
                    f"{clean_text(row.get('for_strat_certainty'))}; "
                    f"comment="
                    f"{clean_text(row.get('for_strat_comment'))}"
                ),
            )

            if foraging is not None:
                written += 1

            body_mass = to_float(
                row.get("body_mass_value")
            )

            observation_id = write_observation(
                writer,
                observation_id,
                species_id,
                trait_ids["body_mass"],
                body_mass,
                "g",
                "EltonTraits body mass",
                "",
                source_id,
                source_record_id,
                (
                    f"source="
                    f"{clean_text(row.get('body_mass_source'))}; "
                    f"spec_level="
                    f"{clean_text(row.get('body_mass_spec_level'))}"
                ),
            )

            if body_mass is not None:
                written += 1

    print(f"Input rows: {rows:,}")
    print(f"Matched: {matched:,}")
    print(f"Unmatched: {unmatched:,}")
    print(f"Trait observations: {written:,}")

    return observation_id


def main():
    print("Loading Gold data...")

    sources = load_sources()

    animaltraits_source_id = find_source_id(
        sources,
        "AnimalTraits",
    )

    elton_source_id = find_source_id(
        sources,
        "EltonTraits",
    )

    resolutions = load_resolution()

    taxon_to_species = load_species_map()

    elton_species_map = load_elton_name_map(
        taxon_to_species
    )

    trait_ids = build_trait_table()

    observation_id = 0

    with open(
        TRAIT_OBSERVATION_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "id",
                "species_id",
                "trait_id",
                "value_numeric",
                "value_text",
                "unit",
                "context",
                "sample_size",
                "source_id",
                "source_record_id",
                "notes",
            ],
            delimiter="\t",
        )

        writer.writeheader()

        observation_id = build_animal_observations(
            writer,
            trait_ids,
            animaltraits_source_id,
            resolutions,
            observation_id,
        )

        observation_id = build_elton_birds(
            writer,
            trait_ids,
            elton_source_id,
            elton_species_map,
            observation_id,
        )

        observation_id = build_elton_mammals(
            writer,
            trait_ids,
            elton_source_id,
            elton_species_map,
            observation_id,
        )

    print()
    print("GOLD TRAIT BUILD COMPLETE")
    print("=========================")
    print(
        f"Trait definitions: "
        f"{len(trait_ids):,}"
    )
    print(
        f"Trait observations: "
        f"{observation_id:,}"
    )


if __name__ == "__main__":
    main()