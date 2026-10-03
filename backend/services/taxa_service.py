# Handles taxonomy queries for the production API.

from database import read_from_database
from api_models import Classification, TaxonDetail


def get_taxon(taxon_id):
    """Return one taxonomic entity by its internal database ID."""

    query = """
        SELECT
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
            "class" AS class_name,
            "order" AS "order",
            family,
            genus,
            specific_epithet,
            infraspecific_epithet,
            taxon_remarks
        FROM taxon
        WHERE id = ?
        LIMIT 1
    """

    rows = read_from_database(query, (taxon_id,))

    if not rows:
        return None

    row = rows[0]

    classification = Classification(
        kingdom=row["kingdom"],
        phylum=row["phylum"],
        class_name=row["class_name"],
        order=row["order"],
        family=row["family"],
        genus=row["genus"],
        specific_epithet=row["specific_epithet"],
        infraspecific_epithet=row["infraspecific_epithet"],
    )

    return TaxonDetail(
        id=row["id"],
        source_taxon_id=row["source_taxon_id"],
        scientific_name=row["scientific_name"],
        scientific_name_authorship=row["scientific_name_authorship"],
        taxonomic_status=row["taxonomic_status"],
        rank=row["rank"],
        parent_taxon_id=row["parent_taxon_id"],
        accepted_taxon_id=row["accepted_taxon_id"],
        classification=classification,
        taxon_remarks=row["taxon_remarks"],
    )


def get_taxon_children(taxon_id):
    """Return the immediate child taxa of a taxon."""

    query = """
        SELECT
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
            "class" AS class_name,
            "order" AS "order",
            family,
            genus,
            specific_epithet,
            infraspecific_epithet,
            taxon_remarks
        FROM taxon
        WHERE parent_taxon_id = ?
        ORDER BY scientific_name COLLATE NOCASE ASC
    """

    rows = read_from_database(query, (taxon_id,))

    children = []

    for row in rows:
        classification = Classification(
            kingdom=row["kingdom"],
            phylum=row["phylum"],
            class_name=row["class_name"],
            order=row["order"],
            family=row["family"],
            genus=row["genus"],
            specific_epithet=row["specific_epithet"],
            infraspecific_epithet=row["infraspecific_epithet"],
        )

        children.append(
            TaxonDetail(
                id=row["id"],
                source_taxon_id=row["source_taxon_id"],
                scientific_name=row["scientific_name"],
                scientific_name_authorship=row["scientific_name_authorship"],
                taxonomic_status=row["taxonomic_status"],
                rank=row["rank"],
                parent_taxon_id=row["parent_taxon_id"],
                accepted_taxon_id=row["accepted_taxon_id"],
                classification=classification,
                taxon_remarks=row["taxon_remarks"],
            )
        )

    return children