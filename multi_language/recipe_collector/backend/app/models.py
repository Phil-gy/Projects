from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    source_url: str
    image_url: Optional[str] = None
    servings: Optional[str] = None
    total_time: Optional[int] = None
    ingredients: str
    instructions: str
    category: Optional[str] = None
    notes: Optional[str] = None


class RecipeImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id")
    image_url: str
    public_id: Optional[str] = None
    is_cover: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)