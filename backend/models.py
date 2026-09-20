# Defines the Pydantic models used to validate API and Silver-layer data.

from pydantic import BaseModel, Field, field_validator


class Species(BaseModel):
    @field_validator(
        "common_name",
        "scientific_name",
        "kingdom",
        "rank",
        "taxonomic_status",
        mode="before"
    )
    @classmethod
    def cleanup(cls, value):
        if value is None:
            return value
        return value.strip()

    common_name: str | None = Field(default=None, max_length=100)
    scientific_name: str = Field(min_length=1, max_length=150)
    kingdom: str | None = Field(default=None, max_length=50)
    rank: str | None = Field(default=None, max_length=50)
    taxonomic_status: str | None = Field(default=None, max_length=50)


class Explorer(BaseModel):
    @field_validator(
        "name",
        "title",
        "activity_period",
        "nationality",
        mode="before"
    )
    @classmethod
    def cleanup(cls, value):
        return value.strip()

    name: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=150)
    activity_period: str = Field(min_length=1, max_length=50)
    nationality: str = Field(min_length=1, max_length=50)
    expedition_count: int = Field(ge=0)


class SilverTaxon(BaseModel):
    taxon_id: str
    parent_taxon_id: str | None = None
    accepted_taxon_id: str | None = None
    scientific_name: str
    scientific_name_authorship: str | None = None
    taxonomic_status: str
    taxon_rank: str
    kingdom: str | None = None
    phylum: str | None = None
    class_name: str | None = None
    order: str | None = None
    family: str | None = None
    genus: str | None = None
    specific_epithet: str | None = None
    infraspecific_epithet: str | None = None
    taxon_remarks: str | None = None
    source_reference: str | None = None
    dataset_id: str