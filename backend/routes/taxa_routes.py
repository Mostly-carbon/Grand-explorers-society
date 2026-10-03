# HTTP endpoints for browsing the production taxonomy hierarchy.

from fastapi import APIRouter, HTTPException

from services.taxa_service import (
    get_taxon,
    get_taxon_children,
)


router = APIRouter(
    prefix="/taxa",
    tags=["Taxonomy"],
)


@router.get("/{taxon_id}")
def get_taxon_by_id(taxon_id: int):
    """Return a single taxonomic entity."""

    taxon = get_taxon(taxon_id)

    if taxon is None:
        raise HTTPException(
            status_code=404,
            detail="Taxon not found",
        )

    return taxon


@router.get("/{taxon_id}/children")
def get_children(taxon_id: int):
    """Return the immediate children of a taxonomic entity."""

    # Check that the parent taxon exists before querying its children.
    # This distinguishes "valid taxon with no children" from "unknown taxon".
    taxon = get_taxon(taxon_id)

    if taxon is None:
        raise HTTPException(
            status_code=404,
            detail="Taxon not found",
        )

    return {
        "taxon_id": taxon_id,
        "children": get_taxon_children(taxon_id),
    }