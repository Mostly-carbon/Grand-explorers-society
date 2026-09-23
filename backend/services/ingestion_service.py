# Handles external data ingestion, normalization, and Silver dataset generation.

import csv
import sys

from models import (
    SilverAnimalObservation,
    SilverEltonBird,
    SilverEltonMammal,
    SilverTaxon,
    SilverVernacularName,
)


csv.field_size_limit(sys.maxsize)


def read_raw_file(file_path):
    with open(
        file_path,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            yield row


def clean_text(value):
    if value is None:
        return None

    value = value.strip()

    return value if value else None


def to_optional_float(value):
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def to_optional_int(value):
    if value is None:
        return None

    value = value.strip()

    if value == "":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def normalize_taxon(record):
    return SilverTaxon(
        taxon_id=record["dwc:taxonID"],
        parent_taxon_id=record["dwc:parentNameUsageID"] or None,
        accepted_taxon_id=record["dwc:acceptedNameUsageID"] or None,
        scientific_name=record["dwc:scientificName"],
        scientific_name_authorship=(
            record["dwc:scientificNameAuthorship"] or None
        ),
        taxonomic_status=record["dwc:taxonomicStatus"],
        taxon_rank=record["dwc:taxonRank"],
        kingdom=record["dwc:kingdom"] or None,
        phylum=record["dwc:phylum"] or None,
        class_name=record["dwc:class"] or None,
        order=record["dwc:order"] or None,
        family=record["dwc:family"] or None,
        genus=record["dwc:genus"] or None,
        specific_epithet=record["dwc:specificEpithet"] or None,
        infraspecific_epithet=record["dwc:infraspecificEpithet"] or None,
        taxon_remarks=record["dwc:taxonRemarks"] or None,
        source_reference=record["dcterms:references"] or None,
        dataset_id=record["dwc:datasetID"],
    )


def normalize_vernacular(record):
    return SilverVernacularName(
        taxon_id=record["dwc:taxonID"],
        language=record["dcterms:language"],
        vernacular_name=record["dwc:vernacularName"],
        merged=record["clb:merged"].lower() == "true",
    )


def build_taxon_silver(input_path, output_path):
    fieldnames = list(SilverTaxon.model_fields.keys())

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:

        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in read_raw_file(input_path):
            taxon = normalize_taxon(record)
            writer.writerow(taxon.model_dump())


def build_vernacular_silver(input_path, output_path):
    fieldnames = list(SilverVernacularName.model_fields.keys())

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:

        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in read_raw_file(input_path):
            vernacular = normalize_vernacular(record)
            writer.writerow(vernacular.model_dump())


def normalize_animal_observation(record):
    return SilverAnimalObservation(
        phylum=clean_text(record["phylum"]),
        class_name=clean_text(record["class"]),
        order=clean_text(record["order"]),
        family=clean_text(record["family"]),
        genus=clean_text(record["genus"]),
        species=clean_text(record["species"]),
        specific_epithet=clean_text(record["specificEpithet"]),

        sex=clean_text(record["sex"]),
        sample_size=to_optional_int(record["sampleSizeValue"]),

        in_text_reference=clean_text(record["inTextReference"]),
        publication_year=to_optional_int(record["publicationYear"]),
        full_reference=clean_text(record["fullReference"]),

        body_mass=to_optional_float(record["body mass"]),
        body_mass_units=clean_text(record["body mass - units"]),
        body_mass_minimum=to_optional_float(
            record["body mass - minimum"]
        ),
        body_mass_maximum=to_optional_float(
            record["body mass - maximum"]
        ),
        body_mass_method=clean_text(
            record["body mass - method"]
        ),
        body_mass_comments=clean_text(
            record["body mass - comments"]
        ),
        body_mass_metadata_comment=clean_text(
            record["body mass - metadata comment"]
        ),
        original_body_mass=clean_text(
            record["original body mass"]
        ),
        original_body_mass_units=clean_text(
            record["original body mass - units"]
        ),

        metabolic_rate=to_optional_float(
            record["metabolic rate"]
        ),
        metabolic_rate_units=clean_text(
            record["metabolic rate - units"]
        ),
        metabolic_rate_minimum=to_optional_float(
            record["metabolic rate - minimum"]
        ),
        metabolic_rate_maximum=to_optional_float(
            record["metabolic rate - maximum"]
        ),
        metabolic_rate_method=clean_text(
            record["metabolic rate - method"]
        ),
        metabolic_rate_comments=clean_text(
            record["metabolic rate - comments"]
        ),
        metabolic_rate_metadata_comment=clean_text(
            record["metabolic rate - metadata comment"]
        ),
        original_metabolic_rate=to_optional_float(
            record["original metabolic rate"]
        ),
        original_metabolic_rate_units=clean_text(
            record["original metabolic rate - units"]
        ),
        original_respiratory_quotient=to_optional_float(
            record["original respiratoryQuotient"]
        ),
        original_temperature=clean_text(
            record["original temperature"]
        ),

        mass_specific_metabolic_rate=to_optional_float(
            record["mass-specific metabolic rate"]
        ),
        mass_specific_metabolic_rate_units=clean_text(
            record["mass-specific metabolic rate - units"]
        ),

        brain_size=to_optional_float(
            record["brain size"]
        ),
        brain_size_units=clean_text(
            record["brain size - units"]
        ),
        brain_size_minimum=to_optional_float(
            record["brain size - minimum"]
        ),
        brain_size_maximum=to_optional_float(
            record["brain size - maximum"]
        ),
        brain_size_method=clean_text(
            record["brain size - method"]
        ),
        brain_size_comments=clean_text(
            record["brain size - comments"]
        ),
        brain_size_metadata_comment=clean_text(
            record["brain size - metadata comment"]
        ),
        original_brain_size=clean_text(
            record["original brain size"]
        ),
        original_brain_size_units=clean_text(
            record["original brain size - units"]
        ),
    )


def build_animal_traits_silver(input_path, output_path):
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

        reader = csv.DictReader(input_file)

        fieldnames = list(
            SilverAnimalObservation.model_fields.keys()
        )

        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in reader:
            observation = normalize_animal_observation(record)
            writer.writerow(observation.model_dump())


def read_elton_file(file_path):
    # EltonTraits files use CP1252 rather than UTF-8.
    with open(
        file_path,
        "r",
        encoding="cp1252",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file,
            delimiter="\t",
        )

        for row in reader:
            yield row


def normalize_elton_bird(record):
    return SilverEltonBird(
        spec_id=clean_text(record["SpecID"]),
        pass_non_pass=clean_text(record["PassNonPass"]),

        ioc_order=clean_text(record["IOCOrder"]),
        bl_family_latin=clean_text(record["BLFamilyLatin"]),
        bl_family_english=clean_text(record["BLFamilyEnglish"]),
        bl_fam_sequ_id=clean_text(record["BLFamSequID"]),
        taxo=clean_text(record["Taxo"]),

        scientific=clean_text(record["Scientific"]),
        english=clean_text(record["English"]),

        diet_inv=to_optional_float(record["Diet-Inv"]),
        diet_vend=to_optional_float(record["Diet-Vend"]),
        diet_vect=to_optional_float(record["Diet-Vect"]),
        diet_vfish=to_optional_float(record["Diet-Vfish"]),
        diet_vunk=to_optional_float(record["Diet-Vunk"]),
        diet_scav=to_optional_float(record["Diet-Scav"]),
        diet_fruit=to_optional_float(record["Diet-Fruit"]),
        diet_nect=to_optional_float(record["Diet-Nect"]),
        diet_seed=to_optional_float(record["Diet-Seed"]),
        diet_planto=to_optional_float(record["Diet-PlantO"]),
        diet_5cat=clean_text(record["Diet-5Cat"]),
        diet_source=clean_text(record["Diet-Source"]),
        diet_certainty=clean_text(record["Diet-Certainty"]),
        diet_entered_by=clean_text(record["Diet-EnteredBy"]),

        for_strat_watbelowsurf=to_optional_float(
            record["ForStrat-watbelowsurf"]
        ),
        for_strat_wataroundsurf=to_optional_float(
            record["ForStrat-wataroundsurf"]
        ),
        for_strat_ground=to_optional_float(
            record["ForStrat-ground"]
        ),
        for_strat_understory=to_optional_float(
            record["ForStrat-understory"]
        ),
        for_strat_midhigh=to_optional_float(
            record["ForStrat-midhigh"]
        ),
        for_strat_canopy=to_optional_float(
            record["ForStrat-canopy"]
        ),
        for_strat_aerial=to_optional_float(
            record["ForStrat-aerial"]
        ),
        pelagic_specialist=to_optional_float(
            record["PelagicSpecialist"]
        ),

        for_strat_source=clean_text(
            record["ForStrat-Source"]
        ),
        for_strat_spec_level=clean_text(
            record["ForStrat-SpecLevel"]
        ),
        for_strat_entered_by=clean_text(
            record["ForStrat-EnteredBy"]
        ),

        nocturnal=to_optional_float(
            record["Nocturnal"]
        ),

        body_mass_value=to_optional_float(
            record["BodyMass-Value"]
        ),
        body_mass_source=clean_text(
            record["BodyMass-Source"]
        ),
        body_mass_spec_level=clean_text(
            record["BodyMass-SpecLevel"]
        ),
        body_mass_comment=clean_text(
            record["BodyMass-Comment"]
        ),

        record_comment=clean_text(
            record["Record-Comment"]
        ),
    )


def normalize_elton_mammal(record):
    return SilverEltonMammal(
        msw3_id=clean_text(record["MSW3_ID"]),
        scientific=clean_text(record["Scientific"]),

        msw_family_latin=clean_text(
            record["MSWFamilyLatin"]
        ),

        diet_inv=to_optional_float(record["Diet-Inv"]),
        diet_vend=to_optional_float(record["Diet-Vend"]),
        diet_vect=to_optional_float(record["Diet-Vect"]),
        diet_vfish=to_optional_float(record["Diet-Vfish"]),
        diet_vunk=to_optional_float(record["Diet-Vunk"]),
        diet_scav=to_optional_float(record["Diet-Scav"]),
        diet_fruit=to_optional_float(record["Diet-Fruit"]),
        diet_nect=to_optional_float(record["Diet-Nect"]),
        diet_seed=to_optional_float(record["Diet-Seed"]),
        diet_planto=to_optional_float(record["Diet-PlantO"]),
        diet_source=clean_text(record["Diet-Source"]),
        diet_certainty=clean_text(record["Diet-Certainty"]),

        for_strat_value=to_optional_float(
            record["ForStrat-Value"]
        ),
        for_strat_certainty=clean_text(
            record["ForStrat-Certainty"]
        ),
        for_strat_comment=clean_text(
            record["ForStrat-Comment"]
        ),

        activity_nocturnal=to_optional_float(
            record["Activity-Nocturnal"]
        ),
        activity_crepuscular=to_optional_float(
            record["Activity-Crepuscular"]
        ),
        activity_diurnal=to_optional_float(
            record["Activity-Diurnal"]
        ),
        activity_source=clean_text(
            record["Activity-Source"]
        ),
        activity_certainty=clean_text(
            record["Activity-Certainty"]
        ),

        body_mass_value=to_optional_float(
            record["BodyMass-Value"]
        ),
        body_mass_source=clean_text(
            record["BodyMass-Source"]
        ),
        body_mass_spec_level=clean_text(
            record["BodyMass-SpecLevel"]
        ),
    )


def build_elton_bird_silver(input_path, output_path):
    fieldnames = list(
        SilverEltonBird.model_fields.keys()
    )

    with open(
        input_path,
        "r",
        encoding="cp1252",
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
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in reader:
            if not record["Scientific"].strip():
                continue

            bird = normalize_elton_bird(record)
            writer.writerow(bird.model_dump())


def build_elton_mammal_silver(input_path, output_path):
    fieldnames = list(
        SilverEltonMammal.model_fields.keys()
    )

    with open(
        input_path,
        "r",
        encoding="cp1252",
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
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in reader:
            if not record["Scientific"].strip():
                continue

            mammal = normalize_elton_mammal(record)
            writer.writerow(mammal.model_dump())