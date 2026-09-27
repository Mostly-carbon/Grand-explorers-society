# Creates the production SQLite database schema for Grand Explorer's Society.

import sqlite3
from pathlib import Path


DATABASE_PATH = Path("grand_explorers_society.db")


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    accessed_at TEXT
);

CREATE TABLE IF NOT EXISTS taxon (
    id INTEGER PRIMARY KEY,
    source_taxon_id TEXT NOT NULL UNIQUE,
    scientific_name TEXT NOT NULL,
    scientific_name_authorship TEXT,
    taxonomic_status TEXT NOT NULL,
    rank TEXT NOT NULL,

    parent_taxon_id INTEGER,
    accepted_taxon_id INTEGER,

    kingdom TEXT,
    phylum TEXT,
    class TEXT,
    "order" TEXT,
    family TEXT,
    genus TEXT,
    specific_epithet TEXT,
    infraspecific_epithet TEXT,
    taxon_remarks TEXT,

    FOREIGN KEY (parent_taxon_id) REFERENCES taxon(id),
    FOREIGN KEY (accepted_taxon_id) REFERENCES taxon(id)
);

CREATE TABLE IF NOT EXISTS species (
    id INTEGER PRIMARY KEY,
    taxon_id INTEGER NOT NULL UNIQUE,

    description TEXT,
    diet TEXT,
    lifespan TEXT,
    status TEXT NOT NULL,

    FOREIGN KEY (taxon_id) REFERENCES taxon(id)
);

CREATE TABLE IF NOT EXISTS vernacular_name (
    id INTEGER PRIMARY KEY,
    taxon_id INTEGER NOT NULL,
    language TEXT,
    name TEXT NOT NULL,
    merged INTEGER NOT NULL,

    FOREIGN KEY (taxon_id) REFERENCES taxon(id)
);

CREATE TABLE IF NOT EXISTS trait (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS trait_observation (
    id INTEGER PRIMARY KEY,
    species_id INTEGER NOT NULL,
    trait_id INTEGER NOT NULL,

    value_numeric REAL,
    value_text TEXT,
    unit TEXT,

    context TEXT,
    sample_size INTEGER,

    source_id INTEGER NOT NULL,
    source_record_id TEXT,
    notes TEXT,

    FOREIGN KEY (species_id) REFERENCES species(id),
    FOREIGN KEY (trait_id) REFERENCES trait(id),
    FOREIGN KEY (source_id) REFERENCES source(id)
);

CREATE INDEX IF NOT EXISTS idx_taxon_parent
    ON taxon(parent_taxon_id);

CREATE INDEX IF NOT EXISTS idx_taxon_accepted
    ON taxon(accepted_taxon_id);

CREATE INDEX IF NOT EXISTS idx_taxon_scientific_name
    ON taxon(scientific_name);

CREATE INDEX IF NOT EXISTS idx_taxon_rank
    ON taxon(rank);

CREATE INDEX IF NOT EXISTS idx_species_taxon
    ON species(taxon_id);

CREATE INDEX IF NOT EXISTS idx_vernacular_taxon
    ON vernacular_name(taxon_id);

CREATE INDEX IF NOT EXISTS idx_vernacular_language
    ON vernacular_name(language);

CREATE INDEX IF NOT EXISTS idx_vernacular_name
    ON vernacular_name(name);

CREATE INDEX IF NOT EXISTS idx_trait_observation_species
    ON trait_observation(species_id);

CREATE INDEX IF NOT EXISTS idx_trait_observation_trait
    ON trait_observation(trait_id);

CREATE INDEX IF NOT EXISTS idx_trait_observation_source
    ON trait_observation(source_id);

CREATE INDEX IF NOT EXISTS idx_trait_observation_species_trait
    ON trait_observation(species_id, trait_id);
"""


def main():
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()

    print(f"Database created: {DATABASE_PATH.resolve()}")


if __name__ == "__main__":
    main()