# Builds the Silver taxon dataset from the raw Catalogue of Life archive.

from services.ingestion_service import build_taxon_silver


input_path = "data/raw/col_dwca/Taxon.tsv"
output_path = "data/silver/taxon.tsv"


build_taxon_silver(input_path, output_path)

print("Taxon Silver dataset built.")