# Handles species queries and assembles product-shaped species responses.

from database import read_from_database
from api_models import (
    Classification,
    SpeciesAbout,
    SpeciesBiology,
    SpeciesDetail,
    SpeciesIdentity,
    SpeciesSummary,
    TraitObservation,
    VernacularName,
)


# Only approved database columns can be used for dynamic sorting.
# User input is mapped through this whitelist rather than inserted into SQL.
SORT_COLUMNS = {
    "scientific_name": "t.scientific_name",
    "rank": "t.rank",
    "kingdom": "t.kingdom",
    "taxonomic_status": "t.taxonomic_status",
    "status": "s.status",
}


def get_species(
    q=None,
    kingdom=None,
    rank=None,
    taxonomic_status=None,
    language=None,
    sort="scientific_name",
    order="asc",
    limit=50,
    offset=0,
):
    """Return a paginated species catalogue."""

    if sort not in SORT_COLUMNS:
        raise ValueError(
            f"Invalid sort option: {sort}. "
            f"Valid options are: {', '.join(SORT_COLUMNS)}"
        )

    if order.lower() not in {"asc", "desc"}:
        raise ValueError("Invalid order. Valid options are: asc, desc")

    if not 1 <= limit <= 200:
        raise ValueError("Limit must be between 1 and 200")

    if offset < 0:
        raise ValueError("Offset cannot be negative")

    conditions = []
    parameters = []

    # Search both scientific and vernacular names so the catalogue can be
    # discovered using either scientific terminology or familiar names.
    if q:
        conditions.append(
            """
            (
                t.scientific_name COLLATE NOCASE LIKE ?
                OR EXISTS (
                    SELECT 1
                    FROM vernacular_name vn
                    WHERE vn.taxon_id = t.id
                      AND vn.name COLLATE NOCASE LIKE ?
                )
            )
            """
        )

        search_value = f"%{q}%"
        parameters.extend([search_value, search_value])

    if kingdom:
        conditions.append("t.kingdom COLLATE NOCASE = ?")
        parameters.append(kingdom)

    if rank:
        conditions.append("t.rank COLLATE NOCASE = ?")
        parameters.append(rank)

    if taxonomic_status:
        conditions.append("t.taxonomic_status COLLATE NOCASE = ?")
        parameters.append(taxonomic_status)

    if language:
        conditions.append(
            """
            EXISTS (
                SELECT 1
                FROM vernacular_name vn
                WHERE vn.taxon_id = t.id
                  AND vn.language COLLATE NOCASE = ?
            )
            """
        )
        parameters.append(language)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # Count the full result set separately so the frontend knows how many
    # records exist beyond the current page.
    count_query = f"""
        SELECT COUNT(*)
        FROM species s
        JOIN taxon t ON t.id = s.taxon_id
        {where_clause}
    """

    count_result = read_from_database(count_query, tuple(parameters))
    total = count_result[0][0]

    query = f"""
        SELECT
            s.id,
            t.scientific_name,
            t.scientific_name_authorship,
            t.rank,
            t.kingdom,
            t.taxonomic_status,
            s.status
        FROM species s
        JOIN taxon t ON t.id = s.taxon_id
        {where_clause}
        ORDER BY {SORT_COLUMNS[sort]} COLLATE NOCASE {order.upper()}
        LIMIT ? OFFSET ?
    """

    query_parameters = parameters + [limit, offset]

    rows = read_from_database(query, tuple(query_parameters))

    species = [
        SpeciesSummary(
            id=row["id"],
            scientific_name=row["scientific_name"],
            scientific_name_authorship=row["scientific_name_authorship"],
            rank=row["rank"],
            kingdom=row["kingdom"],
            taxonomic_status=row["taxonomic_status"],
            status=row["status"],
        )
        for row in rows
    ]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "species": species,
    }


def get_species_detail(scientific_name):
    """Build the complete product-shaped species archive."""

    query = """
        SELECT
            s.id AS species_id,
            s.description,
            s.diet,
            s.lifespan,
            s.status,

            t.id AS taxon_id,
            t.scientific_name,
            t.scientific_name_authorship,
            t.taxonomic_status,
            t.rank,
            t.kingdom,
            t.phylum,
            t."class" AS class_name,
            t."order" AS "order",
            t.family,
            t.genus,
            t.specific_epithet,
            t.infraspecific_epithet,
            t.taxon_remarks
        FROM species s
        JOIN taxon t ON t.id = s.taxon_id
        WHERE t.scientific_name COLLATE NOCASE = ?
        LIMIT 1
    """

    rows = read_from_database(query, (scientific_name,))

    if not rows:
        return None

    row = rows[0]

    names = _get_species_names(row["taxon_id"])
    traits = _get_species_traits(row["species_id"])

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

    identity = SpeciesIdentity(
        scientific_name=row["scientific_name"],
        scientific_name_authorship=row["scientific_name_authorship"],
        taxonomic_status=row["taxonomic_status"],
        rank=row["rank"],
    )

    about = SpeciesAbout(
        description=row["description"],
        diet=row["diet"],
        lifespan=row["lifespan"],
        status=row["status"],
    )

    biology = SpeciesBiology(
        traits=traits
    )

    return SpeciesDetail(
        id=row["species_id"],
        identity=identity,
        about=about,
        biology=biology,
        classification=classification,
        names=names,
    )


def _get_species_names(taxon_id):
    """Retrieve vernacular names associated with a species taxon."""

    query = """
        SELECT
            language,
            name,
            merged
        FROM vernacular_name
        WHERE taxon_id = ?
        ORDER BY
            merged ASC,
            name COLLATE NOCASE ASC
    """

    rows = read_from_database(query, (taxon_id,))

    return [
        VernacularName(
            language=row["language"],
            name=row["name"],
            merged=bool(row["merged"]),
        )
        for row in rows
    ]


def _get_species_traits(species_id):
    """Retrieve biological observations together with their provenance."""

    query = """
        SELECT
            tr.name AS trait,
            tr.category,
            obs.value_numeric,
            obs.value_text,
            obs.unit,
            obs.context,
            obs.sample_size,
            src.name AS source,
            obs.source_record_id,
            obs.notes
        FROM trait_observation obs
        JOIN trait tr ON tr.id = obs.trait_id
        JOIN source src ON src.id = obs.source_id
        WHERE obs.species_id = ?
        ORDER BY
            tr.category COLLATE NOCASE ASC,
            tr.name COLLATE NOCASE ASC,
            obs.id ASC
    """

    rows = read_from_database(query, (species_id,))

    return [
        TraitObservation(
            trait=row["trait"],
            category=row["category"],
            value_numeric=row["value_numeric"],
            value_text=row["value_text"],
            unit=row["unit"],
            context=row["context"],
            sample_size=row["sample_size"],
            source=row["source"],
            source_record_id=row["source_record_id"],
            notes=row["notes"],
        )
        for row in rows
    ]