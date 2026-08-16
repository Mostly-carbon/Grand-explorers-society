from pydantic import BaseModel

class Species(BaseModel):
    name: str
    scientific_name: str
    kingdom: str
    rarity: str
    habitat: str
    lifespan: str
    diet: str
    description: str

