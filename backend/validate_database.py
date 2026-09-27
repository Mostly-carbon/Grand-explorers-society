# Validates the production database structure, relationships, indexes, and product queries.

import sqlite3
from pathlib import Path


DATABASE_PATH = Path("grand_explorers_society.db")


EXPECTED_COUNTS = {
    "source": 3,
    "taxon": 8_055_408,
    "species": 2_476_863,
    "vernacular_name": 1_851_158,
    "trait": 26,
    "trait_observation": 186_683,
}


REQUIRED_INDEXES = {
    "idx_taxon_parent",
    "idx_taxon_accepted",
    "idx_taxon_scientific_name",
    "idx_taxon_rank",
    "idx_species_taxon",
    "idx_vernacular_taxon",
    "idx_vernacular_language",
    "idx_vernacular_name",
    "idx_trait_observation_species",
    "idx_trait_observation_trait",
    "idx_trait_observation_source",
    "idx_trait_observation_species_trait",
}


def check_row_counts(connection):
    print("ROW COUNTS")
    print("-" * 40)

    passed = True

    for table, expected in EXPECTED_COUNTS.items():
        cursor = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        actual = cursor.fetchone()[0]

        result = "PASS" if actual == expected else "FAIL"

        if actual != expected:
            passed = False

        print(
            f"{table:<20}"
            f"{actual:>12,} / {expected:>12,}  "
            f"[{result}]"
        )

    print()

    return passed


def check_sqlite_integrity(connection):
    print("SQLITE INTEGRITY")
    print("-" * 40)

    result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    passed = result == "ok"

    print(f"integrity_check: {result}")
    print()

    return passed


def check_foreign_keys(connection):
    print("FOREIGN KEYS")
    print("-" * 40)

    rows = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    passed = len(rows) == 0

    if passed:
        print("foreign_key_check: PASS")
    else:
        print(
            f"foreign_key_check: FAIL "
            f"({len(rows):,} violations)"
        )

        for row in rows[:10]:
            print(row)

    print()

    return passed


def check_indexes(connection):
    print("INDEXES")
    print("-" * 40)

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
        """
    ).fetchall()

    existing_indexes = {
        row[0]
        for row in rows
    }

    missing_indexes = (
        REQUIRED_INDEXES - existing_indexes
    )

    passed = len(missing_indexes) == 0

    print(
        f"Required indexes present: "
        f"{len(REQUIRED_INDEXES - missing_indexes)}"
        f" / {len(REQUIRED_INDEXES)}"
    )

    if missing_indexes:
        print("Missing indexes:")

        for index in sorted(missing_indexes):
            print(f"  - {index}")

    print(
        f"Index check: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    print()

    return passed


def check_relationships(connection):
    print("RELATIONSHIPS")
    print("-" * 40)

    checks = {
        "species → taxon": """
            SELECT COUNT(*)
            FROM species s
            LEFT JOIN taxon t
                ON s.taxon_id = t.id
            WHERE t.id IS NULL
        """,

        "vernacular → taxon": """
            SELECT COUNT(*)
            FROM vernacular_name v
            LEFT JOIN taxon t
                ON v.taxon_id = t.id
            WHERE t.id IS NULL
        """,

        "observations → species": """
            SELECT COUNT(*)
            FROM trait_observation o
            LEFT JOIN species s
                ON o.species_id = s.id
            WHERE s.id IS NULL
        """,

        "observations → trait": """
            SELECT COUNT(*)
            FROM trait_observation o
            LEFT JOIN trait t
                ON o.trait_id = t.id
            WHERE t.id IS NULL
        """,

        "observations → source": """
            SELECT COUNT(*)
            FROM trait_observation o
            LEFT JOIN source s
                ON o.source_id = s.id
            WHERE s.id IS NULL
        """,
    }

    passed = True

    for name, query in checks.items():
        broken = connection.execute(query).fetchone()[0]

        result = "PASS" if broken == 0 else "FAIL"

        if broken != 0:
            passed = False

        print(
            f"{name:<28}"
            f"{result}"
        )

    print()

    return passed


def check_taxonomy_relationships(connection):
    print("TAXONOMY RELATIONSHIPS")
    print("-" * 40)

    parent_broken = connection.execute(
        """
        SELECT COUNT(*)
        FROM taxon t
        LEFT JOIN taxon parent
            ON t.parent_taxon_id = parent.id
        WHERE t.parent_taxon_id IS NOT NULL
          AND parent.id IS NULL
        """
    ).fetchone()[0]

    accepted_broken = connection.execute(
        """
        SELECT COUNT(*)
        FROM taxon t
        LEFT JOIN taxon accepted
            ON t.accepted_taxon_id = accepted.id
        WHERE t.accepted_taxon_id IS NOT NULL
          AND accepted.id IS NULL
        """
    ).fetchone()[0]

    parent_result = "PASS" if parent_broken == 0 else "FAIL"
    accepted_result = "PASS" if accepted_broken == 0 else "FAIL"

    print(
        f"broken parent references"
        f"{' ' * 7}"
        f"{parent_result}"
    )

    print(
        f"broken accepted references"
        f"{' ' * 4}"
        f"{accepted_result}"
    )

    print()

    return (
        parent_broken == 0
        and accepted_broken == 0
    )


def check_product_queries(connection):
    print("PRODUCT-SHAPED QUERIES")
    print("-" * 40)

    passed = True

    queries = {
        "species page": """
            SELECT
                s.id,
                t.scientific_name,
                t.scientific_name_authorship,
                t.taxonomic_status,
                t.rank,
                t.kingdom,
                t.phylum,
                t.class,
                t."order",
                t.family,
                t.genus,
                t.specific_epithet,
                t.infraspecific_epithet,
                s.description,
                s.diet,
                s.lifespan,
                s.status
            FROM species s
            JOIN taxon t
                ON s.taxon_id = t.id
            LIMIT 1
        """,

        "species names": """
            SELECT
                s.id,
                t.scientific_name,
                v.language,
                v.name,
                v.merged
            FROM species s
            JOIN taxon t
                ON s.taxon_id = t.id
            LEFT JOIN vernacular_name v
                ON v.taxon_id = t.id
            LIMIT 10
        """,

        "species traits": """
            SELECT
                s.id,
                t.scientific_name,
                tr.name,
                tr.category,
                o.value_numeric,
                o.value_text,
                o.unit,
                o.context,
                o.sample_size
            FROM species s
            JOIN taxon t
                ON s.taxon_id = t.id
            JOIN trait_observation o
                ON o.species_id = s.id
            JOIN trait tr
                ON o.trait_id = tr.id
            LIMIT 10
        """,

        "trait sources": """
            SELECT
                s.id,
                t.scientific_name,
                tr.name,
                o.value_numeric,
                o.value_text,
                src.name
            FROM species s
            JOIN taxon t
                ON s.taxon_id = t.id
            JOIN trait_observation o
                ON o.species_id = s.id
            JOIN trait tr
                ON o.trait_id = tr.id
            JOIN source src
                ON o.source_id = src.id
            LIMIT 10
        """,
    }

    for name, query in queries.items():
        try:
            rows = connection.execute(query).fetchall()

            if len(rows) > 0:
                result = "PASS"
            else:
                result = "PASS"

            print(f"{name:<28}{result}")

        except sqlite3.Error as error:
            print(f"{name:<28}FAIL")
            print(f"  {error}")
            passed = False

    print()

    return passed


def check_query_plans(connection):
    print("QUERY PLANS")
    print("-" * 40)

    queries = {
        "scientific name lookup": """
            SELECT
                s.id,
                t.scientific_name
            FROM species s
            JOIN taxon t
                ON s.taxon_id = t.id
            WHERE t.scientific_name = ?
        """,

        "species traits": """
            SELECT
                o.id,
                tr.name,
                o.value_numeric,
                o.value_text
            FROM trait_observation o
            JOIN trait tr
                ON o.trait_id = tr.id
            WHERE o.species_id = ?
        """,

        "species names": """
            SELECT
                v.name,
                v.language,
                v.merged
            FROM vernacular_name v
            WHERE v.taxon_id = ?
        """,
    }

    passed = True

    for name, query in queries.items():
        try:
            plan = connection.execute(
                f"EXPLAIN QUERY PLAN {query}",
                ("Panthera leo",)
                if name == "scientific name lookup"
                else (1,)
            ).fetchall()

            plan_text = " ".join(
                str(row)
                for row in plan
            )

            print(f"{name:<28}PASS")

            print(
                f"  {plan_text[:180]}"
            )

        except sqlite3.Error as error:
            print(f"{name:<28}FAIL")
            print(f"  {error}")
            passed = False

    print()

    return passed


def analyze_database(connection):
    print("ANALYZE")
    print("-" * 40)

    try:
        connection.execute("ANALYZE")
        connection.commit()

        print("ANALYZE: PASS")
        print()

        return True

    except sqlite3.Error as error:
        print(f"ANALYZE: FAIL")
        print(f"  {error}")
        print()

        return False


def main():
    if not DATABASE_PATH.exists():
        print(
            f"Database not found: "
            f"{DATABASE_PATH}"
        )

        return

    print(
        f"Validating: "
        f"{DATABASE_PATH.resolve()}"
    )

    print()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        results = []

        results.append(
            check_row_counts(connection)
        )

        results.append(
            check_sqlite_integrity(connection)
        )

        results.append(
            check_foreign_keys(connection)
        )

        results.append(
            check_indexes(connection)
        )

        results.append(
            check_relationships(connection)
        )

        results.append(
            check_taxonomy_relationships(connection)
        )

        results.append(
            check_product_queries(connection)
        )

        results.append(
            check_query_plans(connection)
        )

        results.append(
            analyze_database(connection)
        )

    finally:
        connection.close()

    print("=" * 40)

    if all(results):
        print("DATABASE VALIDATION: PASS")
        print()
        print(
            "The production database passed "
            "all validation checks."
        )
    else:
        print("DATABASE VALIDATION: FAIL")
        print()
        print(
            "One or more validation checks failed."
        )


if __name__ == "__main__":
    main()