# Defines Pydantic models for the public API responses.
# These are separate from models.py, which validates Silver/source data.

from pydantic import BaseModel


class SpeciesSummary(BaseModel):
    """Lightweight species record used by the species catalogue."""

    id: int
    scientific_name: str
    scientific_name_authorship: str | None = None
    rank: str
    kingdom: str | None = None
    taxonomic_status: str
    status: str


class VernacularName(BaseModel):
    """A common/vernacular name associated with a taxon."""

    language: str | None = None
    name: str
    merged: bool


class TraitObservation(BaseModel):
    """One biological observation, including its source."""

    trait: str
    category: str
    value_numeric: float | None = None
    value_text: str | None = None
    unit: str | None = None
    context: str | None = None
    sample_size: int | None = None
    source: str
    source_record_id: str | None = None
    notes: str | None = None


class Classification(BaseModel):
    """The standard taxonomic hierarchy for a species."""

    kingdom: str | None = None
    phylum: str | None = None
    class_name: str | None = None
    order: str | None = None
    family: str | None = None
    genus: str | None = None
    specific_epithet: str | None = None
    infraspecific_epithet: str | None = None


class SpeciesIdentity(BaseModel):
    """Identity information displayed at the top of a species archive."""

    scientific_name: str
    scientific_name_authorship: str | None = None
    taxonomic_status: str
    rank: str


class SpeciesAbout(BaseModel):
    """Readable product-level information about the species."""

    description: str | None = None
    diet: str | None = None
    lifespan: str | None = None
    status: str


class SpeciesBiology(BaseModel):
    """Biological observations collected from the available sources."""

    traits: list[TraitObservation]


class SpeciesDetail(BaseModel):
    """Complete product-shaped species archive."""

    id: int
    identity: SpeciesIdentity
    about: SpeciesAbout
    biology: SpeciesBiology
    classification: Classification
    names: list[VernacularName]


class TaxonDetail(BaseModel):
    """Product representation of a taxonomic entity."""

    id: int
    source_taxon_id: str
    scientific_name: str
    scientific_name_authorship: str | None = None
    taxonomic_status: str
    rank: str
    parent_taxon_id: int | None = None
    accepted_taxon_id: int | None = None
    classification: Classification
    taxon_remarks: str | None = None