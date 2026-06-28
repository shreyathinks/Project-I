"""
Recipe recommendation service.
Uses SentenceTransformers + FAISS for similarity search (with TF-IDF fallback).
Optionally calls Ollama for LLM-generated recipes.
"""

import json
import logging
import os
from typing import List, Optional

import httpx
import numpy as np
from sqlalchemy.orm import Session

from config.settings import settings
from models.recipe import Recipe

# Ensure HuggingFace uses legacy HTTP download (xet protocol is broken in 1.5.x)
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

logger = logging.getLogger(__name__)

# ── Lazy-loaded globals ───────────────────────────────────────────────────────
_embedder = None
_faiss_index = None
_recipe_ids: List[int] = []
_use_tfidf = False           # set True when SentenceTransformer download fails
_tfidf_vectorizer = None
_tfidf_matrix = None


def _load_embedder():
    """Load SentenceTransformer; sets _use_tfidf=True and returns None on failure."""
    global _embedder, _use_tfidf
    if _use_tfidf:
        return None
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(
                "all-MiniLM-L6-v2",
                cache_folder=settings.models_cache_dir,
            )
        except Exception as exc:
            logger.warning("SentenceTransformer unavailable (%s). Switching to TF-IDF.", exc)
            _use_tfidf = True
            return None
    return _embedder


def _build_tfidf_index(recipes):
    """Build a TF-IDF matrix as a fallback when the neural embedder is unavailable."""
    global _tfidf_vectorizer, _tfidf_matrix, _recipe_ids
    from sklearn.feature_extraction.text import TfidfVectorizer
    texts = [f"{r.title} {r.ingredients}" for r in recipes]
    _tfidf_vectorizer = TfidfVectorizer(stop_words="english")
    _tfidf_matrix = _tfidf_vectorizer.fit_transform(texts)
    _recipe_ids = [r.id for r in recipes]
    logger.info("TF-IDF index built with %d recipes", len(recipes))


def _build_faiss_index(db: Session):
    """Build FAISS index from all recipes in DB. Falls back to TF-IDF."""
    global _faiss_index, _recipe_ids
    import faiss

    recipes = db.query(Recipe).all()
    if not recipes:
        return

    embedder = _load_embedder()
    if embedder is None:
        _build_tfidf_index(recipes)
        return

    texts = [f"{r.title} {r.ingredients}" for r in recipes]
    embeddings = np.array(
        embedder.encode(texts, show_progress_bar=False), dtype=np.float32
    )

    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    _faiss_index = index
    _recipe_ids = [r.id for r in recipes]
    logger.info("FAISS index built with %d recipes", len(recipes))


def _get_faiss_index(db: Session):
    global _faiss_index
    if _faiss_index is None and not _use_tfidf:
        _build_faiss_index(db)
    if _use_tfidf and _tfidf_matrix is None:
        recipes = db.query(Recipe).all()
        if recipes:
            _build_tfidf_index(recipes)
    return _faiss_index


class RecipeService:

    @staticmethod
    def recommend(
        db: Session,
        available_ingredients: List[str],
        filter_vegetarian: bool = False,
        filter_vegan: bool = False,
        filter_high_protein: bool = False,
        max_cooking_time: Optional[int] = None,
        top_k: int = 5,
    ) -> List[Recipe]:
        _get_faiss_index(db)  # ensure index (or TF-IDF) is built

        query_text = " ".join(available_ingredients)
        candidate_ids = []

        if _use_tfidf and _tfidf_vectorizer is not None:
            # TF-IDF cosine similarity fallback
            from sklearn.metrics.pairwise import cosine_similarity
            q_vec = _tfidf_vectorizer.transform([query_text])
            scores = cosine_similarity(q_vec, _tfidf_matrix).flatten()
            top_indices = scores.argsort()[::-1][:top_k * 4]
            candidate_ids = [_recipe_ids[i] for i in top_indices if i < len(_recipe_ids)]
        elif _faiss_index is not None and _recipe_ids:
            import faiss
            embedder = _load_embedder()
            if embedder is None:
                return db.query(Recipe).limit(top_k).all()
            q_vec = np.array(
                embedder.encode([query_text], show_progress_bar=False), dtype=np.float32
            )
            faiss.normalize_L2(q_vec)
            k = min(top_k * 4, len(_recipe_ids))
            _, indices = _faiss_index.search(q_vec, k)
            candidate_ids = [_recipe_ids[i] for i in indices[0] if i < len(_recipe_ids)]
        else:
            return db.query(Recipe).limit(top_k).all()

        candidates = db.query(Recipe).filter(Recipe.id.in_(candidate_ids)).all()

        if filter_vegetarian:
            candidates = [r for r in candidates if r.is_vegetarian]
        if filter_vegan:
            candidates = [r for r in candidates if r.is_vegan]
        if filter_high_protein:
            candidates = [r for r in candidates if r.is_high_protein]
        if max_cooking_time:
            candidates = [r for r in candidates if r.cooking_time_minutes and r.cooking_time_minutes <= max_cooking_time]

        return candidates[:top_k]

    @staticmethod
    async def generate_with_ollama(ingredients: List[str]) -> Optional[str]:
        """
        Call Ollama local LLM to generate a recipe from available ingredients.
        Returns None if Ollama is unavailable.
        """
        prompt = (
            f"Create a detailed recipe using these ingredients: {', '.join(ingredients)}. "
            "Include: recipe name, ingredients list with quantities, step-by-step instructions, "
            "cooking time, and serving suggestions. Be concise but complete."
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{settings.ollama_host}/api/generate",
                    json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                return resp.json().get("response")
        except Exception as exc:
            logger.warning("Ollama unavailable (%s). Using FAISS results only.", exc)
            return None

    @staticmethod
    def load_recipes_from_dataset(db: Session) -> int:
        """Load recipes from datasets/recipes.json into the DB if empty."""
        if db.query(Recipe).count() > 0:
            return 0

        dataset_path = os.path.join(settings.datasets_dir, "recipes.json")
        if not os.path.exists(dataset_path):
            logger.warning("datasets/recipes.json not found")
            return 0

        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = 0
        for item in data:
            recipe = Recipe(
                title=item["title"],
                description=item.get("description"),
                ingredients=json.dumps(item["ingredients"]),
                instructions=item["instructions"],
                cooking_time_minutes=item.get("cooking_time_minutes"),
                servings=item.get("servings", 2),
                cuisine=item.get("cuisine"),
                category=item.get("category"),
                is_vegetarian=item.get("is_vegetarian", False),
                is_vegan=item.get("is_vegan", False),
                is_high_protein=item.get("is_high_protein", False),
                is_gluten_free=item.get("is_gluten_free", False),
                calories=item.get("calories"),
                image_url=item.get("image_url"),
            )
            db.add(recipe)
            count += 1

        db.commit()
        logger.info("Loaded %d recipes from dataset", count)

        # Invalidate FAISS index so it rebuilds
        global _faiss_index, _recipe_ids
        _faiss_index = None
        _recipe_ids = []

        return count

    @staticmethod
    def rebuild_index(db: Session):
        """Force rebuild of FAISS index."""
        global _faiss_index, _recipe_ids
        _faiss_index = None
        _recipe_ids = []
        _build_faiss_index(db)
