
"""Handles species queries and assembles product-shaped species responses."""

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
SORT_COLUMNS = {
    "scientific_name": "t.scientific_name",
    "rank": "t.rank",
    "kingdom": "t.kingdom",
    "taxonomic_status": "t.taxonomic_status",
    "status": "s.status",
}

# Search results are delivered in batches, with a hard cap across pages.
MAX_SEARCH_RESULTS = 500
SEARCH_COUNT_CAP = MAX_SEARCH_RESULTS + 1


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

    if not isinstance(order, str) or order.lower() not in {"asc", "desc"}:
        raise ValueError("Invalid order. Valid options are: asc, desc")

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 200
    ):
        raise ValueError("Limit must be between 1 and 200")

    if (
        not isinstance(offset, int)
        or isinstance(offset, bool)
        or offset < 0
    ):
        raise ValueError("Offset cannot be negative")

    order = order.upper()
    q = q.strip() if isinstance(q, str) else q

    conditions = []
    parameters = []

    if q:
        search_value = f"%{q}%"

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

    # Preserve exact totals for unfiltered and non-text-filtered catalogues.
    # Text searches count at most 501 matches.
    if q:
        count_query = f"""
            SELECT COUNT(*)
            FROM (
                SELECT 1
                FROM species s
                JOIN taxon t ON t.id = s.taxon_id
                {where_clause}
                LIMIT ?
            )
        """
        count_parameters = tuple(parameters + [SEARCH_COUNT_CAP])

    elif not conditions:
        count_query = "SELECT COUNT(*) FROM species"
        count_parameters = ()

    else:
        count_query = f"""
            SELECT COUNT(*)
            FROM species s
            JOIN taxon t ON t.id = s.taxon_id
            {where_clause}
        """
        count_parameters = tuple(parameters)

    count_result = read_from_database(
        count_query,
        count_parameters,
    )
    total = count_result[0][0]

    # Do not return search records beyond the global cap.
    # Fetch one extra row to determine whether another batch exists.
    if q:
        if offset >= MAX_SEARCH_RESULTS:
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "species": [],
                "has_more": False,
            }

        fetch_limit = min(
            limit + 1,
            MAX_SEARCH_RESULTS - offset + 1,
        )
    else:
        fetch_limit = limit + 1

    if q:
        exact_vernacular = """
            EXISTS (
                SELECT 1
                FROM vernacular_name vn
                WHERE vn.taxon_id = t.id
                  AND vn.name COLLATE NOCASE = ?
            )
        """

        exact_scientific = """
            (
                t.scientific_name COLLATE NOCASE = ?
                OR (
                    t.genus || ' ' || t.specific_epithet
                ) COLLATE NOCASE = ?
            )
        """

        scientific_starts = """
            t.scientific_name COLLATE NOCASE LIKE ?
        """

        vernacular_starts = """
            EXISTS (
                SELECT 1
                FROM vernacular_name vn
                WHERE vn.taxon_id = t.id
                  AND vn.name COLLATE NOCASE LIKE ?
            )
        """

        scientific_contains = """
            t.scientific_name COLLATE NOCASE LIKE ?
        """

        vernacular_contains = """
            EXISTS (
                SELECT 1
                FROM vernacular_name vn
                WHERE vn.taxon_id = t.id
                  AND vn.name COLLATE NOCASE LIKE ?
            )
        """

        relevance_query = f"""
            CASE
                WHEN {exact_vernacular} THEN 1
                WHEN {exact_scientific} THEN 2
                WHEN {scientific_starts} THEN 3
                WHEN {vernacular_starts} THEN 4
                WHEN {scientific_contains} THEN 5
                WHEN {vernacular_contains} THEN 6
                ELSE 7
            END
        """

        relevance_parameters = [
            q,
            q,
            q,
            f"{q}%",
            f"{q}%",
            f"%{q}%",
            f"%{q}%",
        ]

        query_parameters = (
            parameters
            + relevance_parameters
            + [fetch_limit, offset]
        )

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
            ORDER BY
                {relevance_query},
                {SORT_COLUMNS[sort]} COLLATE NOCASE {order}
            LIMIT ? OFFSET ?
        """

    else:
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
            ORDER BY
                {SORT_COLUMNS[sort]} COLLATE NOCASE {order}
            LIMIT ? OFFSET ?
        """

        query_parameters = parameters + [fetch_limit, offset]

    rows = read_from_database(
        query,
        tuple(query_parameters),
    )

    # The extra row indicates that another batch exists.
    has_more = len(rows) > limit
    rows = rows[:limit]

    # Enforce the global search cap, including the final batch.
    if q:
        remaining = MAX_SEARCH_RESULTS - offset
        rows = rows[:max(0, remaining)]

        has_more = (
            offset + len(rows) < MAX_SEARCH_RESULTS
            and has_more
        )

    species = []

    for row in rows:
        scientific_name = row["scientific_name"]
        authorship = row["scientific_name_authorship"]

        if authorship and scientific_name.endswith(authorship):
            scientific_name = scientific_name[:-len(authorship)].strip()

        species.append(
            SpeciesSummary(
                id=row["id"],
                scientific_name=scientific_name,
                scientific_name_authorship=authorship,
                rank=row["rank"],
                kingdom=row["kingdom"],
                taxonomic_status=row["taxonomic_status"],
                status=row["status"],
            )
        )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "species": species,
        "has_more": has_more,
    }


def get_species_detail(scientific_name):
    """Build the complete product-shaped species archive."""

    # Accept both the scientific name and the name including authorship.
    base_name = scientific_name.split(" (", 1)[0].strip()

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
        WHERE
            LOWER(t.scientific_name) = LOWER(?)
            OR LOWER(t.genus || ' ' || t.specific_epithet) = LOWER(?)
        LIMIT 1
    """

    rows = read_from_database(
        query,
        (base_name, base_name),
    )

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

    scientific_name = row["scientific_name"]
    authorship = row["scientific_name_authorship"]

    if authorship and scientific_name.endswith(authorship):
        scientific_name = scientific_name[:-len(authorship)].strip()

    identity = SpeciesIdentity(
        scientific_name=scientific_name,
        scientific_name_authorship=authorship,
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
        traits=traits,
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
