from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.database import get_db
from models.user import User
from schemas.recipe import RecipeOut, RecipeRecommendRequest, RecipeRecommendResponse
from services.inventory_service import InventoryService
from services.recipe_service import RecipeService
from utils.security import get_current_user

router = APIRouter()


@router.post("/recommend", response_model=RecipeRecommendResponse)
async def recommend_recipes(
    data: RecipeRecommendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recommend recipes based on available ingredients.
    Optionally queries Ollama for a generated recipe.
    """
    ingredients = data.available_ingredients

    # If use_expiring_first, prepend expiring items to ingredient list
    if data.use_expiring_first:
        expiring = InventoryService.get_expiring_items(db, current_user.id, days=5)
        expiring_names = [i.name for i in expiring]
        ingredients = expiring_names + [i for i in ingredients if i not in expiring_names]

    recipes = RecipeService.recommend(
        db,
        available_ingredients=ingredients,
        filter_vegetarian=data.filter_vegetarian,
        filter_vegan=data.filter_vegan,
        filter_high_protein=data.filter_high_protein,
        max_cooking_time=data.max_cooking_time,
        top_k=data.top_k,
    )

    # Try Ollama for an LLM-generated suggestion
    generated = None
    source = "faiss"
    if ingredients:
        generated = await RecipeService.generate_with_ollama(ingredients[:10])
        if generated:
            source = "ollama"

    return RecipeRecommendResponse(
        recipes=recipes,
        generated_recipe=generated,
        source=source,
    )


@router.get("/", response_model=List[RecipeOut])
def list_recipes(
    search: Optional[str] = Query(default=None, max_length=100),
    vegetarian: bool = Query(default=False),
    vegan: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Browse all recipes with optional filters."""
    from models.recipe import Recipe
    query = db.query(Recipe)
    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))
    if vegetarian:
        query = query.filter(Recipe.is_vegetarian == True)
    if vegan:
        query = query.filter(Recipe.is_vegan == True)
    return query.limit(limit).all()


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    from models.recipe import Recipe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/load-dataset")
def load_dataset(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Load recipes from the dataset file into the database."""
    count = RecipeService.load_recipes_from_dataset(db)
    return {"loaded": count}
