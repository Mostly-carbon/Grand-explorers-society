# Builds the Silver vernacular-name dataset from the raw Catalogue of Life archive.

from services.ingestion_service import build_vernacular_silver


input_path = "data/raw/col_dwca/VernacularName.tsv"
output_path = "data/silver/vernacular_name.tsv"


build_vernacular_silver(input_path, output_path)

print("Vernacular Silver dataset built.")