"""
Model training scripts for offline / batch training.
Run directly: python ml/train_models.py
"""

import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_waste_predictor():
    """Train and save the waste risk classifier with synthetic data."""
    import pickle
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score

    logger.info("Training waste predictor...")

    # Expanded synthetic training data
    # Features: [days_until_expiry, quantity, avg_daily, shelf_life_pct, days_since_purchase]
    data = []
    labels = []

    # High risk (2): low days, low consumption, expiry near
    for _ in range(50):
        data.append([
            np.random.randint(-2, 3),
            np.random.uniform(0.5, 8),
            np.random.uniform(0.05, 0.3),
            np.random.uniform(0, 0.1),
            np.random.randint(20, 35),
        ])
        labels.append(2)

    # Medium risk (1)
    for _ in range(50):
        data.append([
            np.random.randint(3, 8),
            np.random.uniform(2, 10),
            np.random.uniform(0.3, 0.8),
            np.random.uniform(0.2, 0.5),
            np.random.randint(10, 20),
        ])
        labels.append(1)

    # Low risk (0)
    for _ in range(50):
        data.append([
            np.random.randint(7, 60),
            np.random.uniform(1, 15),
            np.random.uniform(0.5, 3),
            np.random.uniform(0.5, 1.0),
            np.random.randint(1, 10),
        ])
        labels.append(0)

    X = np.array(data)
    y = np.array(labels)

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=100, random_state=42)),
    ])

    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    logger.info("CV accuracy: %.3f ± %.3f", scores.mean(), scores.std())

    model.fit(X, y)

    os.makedirs(settings.models_cache_dir, exist_ok=True)
    model_path = os.path.join(settings.models_cache_dir, "waste_predictor.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    logger.info("Waste predictor saved to %s", model_path)
    return model


def build_faiss_index_from_dataset():
    """Build and save a FAISS index from the recipes dataset."""
    dataset_path = os.path.join(settings.datasets_dir, "recipes.json")
    if not os.path.exists(dataset_path):
        logger.error("recipes.json not found at %s", dataset_path)
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    logger.info("Building FAISS index for %d recipes...", len(recipes))

    import faiss
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=settings.models_cache_dir)
    texts = [f"{r['title']} {' '.join(r['ingredients'])}" for r in recipes]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype(np.float32)
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_path = os.path.join(settings.models_cache_dir, "recipes.faiss")
    faiss.write_index(index, index_path)

    ids_path = os.path.join(settings.models_cache_dir, "recipe_ids.json")
    with open(ids_path, "w") as f:
        json.dump(list(range(len(recipes))), f)

    logger.info("FAISS index saved to %s", index_path)


if __name__ == "__main__":
    train_waste_predictor()
    build_faiss_index_from_dataset()
    logger.info("All models trained successfully.")
