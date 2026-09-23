# Defines Pydantic models used to validate source data before writing Silver datasets.

from pydantic import BaseModel, Field


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


class SilverVernacularName(BaseModel):
    taxon_id: str
    language: str
    vernacular_name: str
    merged: bool


class SilverAnimalObservation(BaseModel):
    phylum: str | None = None
    class_name: str | None = None
    order: str | None = None
    family: str | None = None
    genus: str | None = None
    species: str | None = None
    specific_epithet: str | None = None

    sex: str | None = None
    sample_size: int | None = Field(default=None, ge=0)

    in_text_reference: str | None = None
    publication_year: int | None = None
    full_reference: str | None = None

    body_mass: float | None = None
    body_mass_units: str | None = None
    body_mass_minimum: float | None = None
    body_mass_maximum: float | None = None
    body_mass_method: str | None = None
    body_mass_comments: str | None = None
    body_mass_metadata_comment: str | None = None

    # Original source values are strings because some contain ranges
    # such as "56-503" rather than a single numeric value.
    original_body_mass: str | None = None
    original_body_mass_units: str | None = None

    metabolic_rate: float | None = None
    metabolic_rate_units: str | None = None
    metabolic_rate_minimum: float | None = None
    metabolic_rate_maximum: float | None = None
    metabolic_rate_method: str | None = None
    metabolic_rate_comments: str | None = None
    metabolic_rate_metadata_comment: str | None = None

    original_metabolic_rate: float | None = None
    original_metabolic_rate_units: str | None = None
    original_respiratory_quotient: float | None = None

    # Original temperature may contain ranges such as "28-35".
    original_temperature: str | None = None

    mass_specific_metabolic_rate: float | None = None
    mass_specific_metabolic_rate_units: str | None = None

    brain_size: float | None = None
    brain_size_units: str | None = None
    brain_size_minimum: float | None = None
    brain_size_maximum: float | None = None
    brain_size_method: str | None = None
    brain_size_comments: str | None = None
    brain_size_metadata_comment: str | None = None
    original_brain_size: float | None = None
    original_brain_size_units: str | None = None


class SilverEltonBird(BaseModel):
    spec_id: str
    pass_non_pass: str | None = None

    ioc_order: str | None = None
    bl_family_latin: str | None = None
    bl_family_english: str | None = None
    bl_fam_sequ_id: str | None = None
    taxo: str | None = None

    scientific: str
    english: str | None = None

    diet_inv: float | None = None
    diet_vend: float | None = None
    diet_vect: float | None = None
    diet_vfish: float | None = None
    diet_vunk: float | None = None
    diet_scav: float | None = None
    diet_fruit: float | None = None
    diet_nect: float | None = None
    diet_seed: float | None = None
    diet_planto: float | None = None
    diet_5cat: str | None = None
    diet_source: str | None = None
    diet_certainty: str | None = None
    diet_entered_by: str | None = None

    for_strat_watbelowsurf: float | None = None
    for_strat_wataroundsurf: float | None = None
    for_strat_ground: float | None = None
    for_strat_understory: float | None = None
    for_strat_midhigh: float | None = None
    for_strat_canopy: float | None = None
    for_strat_aerial: float | None = None
    pelagic_specialist: float | None = None

    for_strat_source: str | None = None
    for_strat_spec_level: str | None = None
    for_strat_entered_by: str | None = None

    nocturnal: float | None = None

    body_mass_value: float | None = None
    body_mass_source: str | None = None
    body_mass_spec_level: str | None = None
    body_mass_comment: str | None = None

    record_comment: str | None = None


class SilverEltonMammal(BaseModel):
    msw3_id: str
    scientific: str

    msw_family_latin: str | None = None

    diet_inv: float | None = None
    diet_vend: float | None = None
    diet_vect: float | None = None
    diet_vfish: float | None = None
    diet_vunk: float | None = None
    diet_scav: float | None = None
    diet_fruit: float | None = None
    diet_nect: float | None = None
    diet_seed: float | None = None
    diet_planto: float | None = None
    diet_source: str | None = None
    diet_certainty: str | None = None

    for_strat_value: float | None = None
    for_strat_certainty: str | None = None
    for_strat_comment: str | None = None

    activity_nocturnal: float | None = None
    activity_crepuscular: float | None = None
    activity_diurnal: float | None = None
    activity_source: str | None = None
    activity_certainty: str | None = None

    body_mass_value: float | None = None
    body_mass_source: str | None = None
    body_mass_spec_level: str | None = None