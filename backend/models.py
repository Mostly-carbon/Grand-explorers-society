from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Allowed rarity values
class Rarity(str, Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    VERY_RARE = "Very rare"
    EXTREMELY_RARE = "Extremely rare"


class Species(BaseModel):

    # Remove surrounding whitespace before validation
    @field_validator("name", "scientific_name", "kingdom", "habitat", "diet", "description", mode="before")
    @classmethod
    def cleanup(cls, value):
        return value.strip()

    name: str = Field(min_length=1, max_length=100)
    scientific_name: str = Field(min_length=1, max_length=150)
    kingdom: str = Field(min_length=1, max_length=50)
    rarity: Rarity
    habitat: str = Field(min_length=1, max_length=100)
    lifespan: str
    diet: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)


class Explorer(BaseModel):

    @field_validator("name", "title", "activity_period", "nationality", mode="before")
    @classmethod
    def cleanup(cls, value):
        return value.strip()

    name: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=150)
    activity_period: str = Field(min_length=1, max_length=50)
    nationality: str = Field(min_length=1, max_length=50)
    expedition_count: int = Field(ge=0)