"""
OCR wrapper — tries PaddleOCR first, falls back to pytesseract.
Exposes a single `extract_text(image_path) -> str` function.
"""

import logging
import os
from typing import List, Tuple

from config.settings import settings

logger = logging.getLogger(__name__)

# ── PaddleOCR lazy loader ──────────────────────────────────────────────────────
_paddle_ocr = None


def _get_paddle():
    global _paddle_ocr
    if _paddle_ocr is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                show_log=False,
                use_gpu=False,
            )
            logger.info("PaddleOCR initialized")
        except ImportError:
            logger.warning("PaddleOCR not available. Will use Tesseract.")
    return _paddle_ocr


def extract_with_paddle(image_path: str) -> str:
    ocr = _get_paddle()
    if ocr is None:
        raise RuntimeError("PaddleOCR not available")

    results = ocr.ocr(image_path, cls=True)
    lines = []
    if results and results[0]:
        for line in results[0]:
            text, confidence = line[1]
            if confidence > 0.6:
                lines.append(text)
    return "\n".join(lines)


def extract_with_tesseract(image_path: str) -> str:
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    # Pre-process: convert to grayscale for better accuracy
    img = img.convert("L")
    return pytesseract.image_to_string(img)


def extract_text(image_path: str) -> str:
    """
    Extract all text from an image file.
    Uses PaddleOCR if available, otherwise falls back to Tesseract.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    engine = settings.ocr_engine.lower()

    if engine == "tesseract":
        return extract_with_tesseract(image_path)

    # Default: try Paddle, fall back to Tesseract
    try:
        return extract_with_paddle(image_path)
    except Exception as paddle_err:
        logger.warning("PaddleOCR failed (%s). Falling back to Tesseract.", paddle_err)
        try:
            return extract_with_tesseract(image_path)
        except Exception as tess_err:
            logger.error("Tesseract also failed: %s", tess_err)
            raise RuntimeError("All OCR engines failed") from tess_err
