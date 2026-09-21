# Handles external data ingestion and preparation for the database.

import csv
import sys

from database import read_from_database, write_to_database
from models import SilverTaxon, SilverVernacularName, Species


csv.field_size_limit(sys.maxsize)


def read_raw_file(file_path):
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")

        for row in reader:
            yield row


def normalize_taxon(record):
    return SilverTaxon(
        taxon_id=record["dwc:taxonID"],
        parent_taxon_id=record["dwc:parentNameUsageID"] or None,
        accepted_taxon_id=record["dwc:acceptedNameUsageID"] or None,
        scientific_name=record["dwc:scientificName"],
        scientific_name_authorship=record["dwc:scientificNameAuthorship"] or None,
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
    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        fieldnames = [
            "taxon_id",
            "parent_taxon_id",
            "accepted_taxon_id",
            "scientific_name",
            "scientific_name_authorship",
            "taxonomic_status",
            "taxon_rank",
            "kingdom",
            "phylum",
            "class_name",
            "order",
            "family",
            "genus",
            "specific_epithet",
            "infraspecific_epithet",
            "taxon_remarks",
            "source_reference",
            "dataset_id",
        ]

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
    fieldnames = [
        "taxon_id",
        "language",
        "vernacular_name",
        "merged",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
            delimiter="\t",
        )

        writer.writeheader()

        for record in read_raw_file(input_path):
            vernacular = normalize_vernacular(record)
            writer.writerow(vernacular.model_dump())

def save_species(species):
    existing = read_from_database(
        "SELECT id FROM species WHERE scientific_name = ?",
        (species.scientific_name,),
    )

    if existing:
        return {
            "status": "already_exists",
            "scientific_name": species.scientific_name,
            "id": existing[0][0],
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
            species.taxonomic_status,
        ),
    )

    return {
        "status": "inserted",
        "scientific_name": species.scientific_name,
    }