# Handles HTTP routes for the production species API.

from fastapi import APIRouter, HTTPException, Query

from services.species_service import (
    get_species,
    get_species_detail,
)


router = APIRouter(
    prefix="/species",
    tags=["Species"],
)


# Returns a paginated species catalogue.
@router.get("/")
def list_species(
    q: str | None = None,
    kingdom: str | None = None,
    rank: str | None = None,
    taxonomic_status: str | None = None,
    language: str | None = None,
    sort: str = "scientific_name",
    order: str = "asc",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        return get_species(
            q=q,
            kingdom=kingdom,
            rank=rank,
            taxonomic_status=taxonomic_status,
            language=language,
            sort=sort,
            order=order,
            limit=limit,
            offset=offset,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# Returns one complete species archive by scientific name.
@router.get("/{scientific_name}")
def get_species_by_name(scientific_name: str):
    species = get_species_detail(scientific_name)

    if species is None:
        raise HTTPException(
            status_code=404,
            detail="Species not found",
        )

    return species