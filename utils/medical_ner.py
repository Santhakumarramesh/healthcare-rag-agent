"""
Medical Named Entity Recognition (NER) Utility

Extracts clinical entities from medical queries using blaze999/Medical-NER.
Lazy-loaded on first use to avoid startup timeout on free-tier hosts.

Recognized entity types:
  DISEASE     - diseases, conditions, diagnoses
  DRUG        - medications, drug names
  SYMPTOM     - patient-reported symptoms
  LABVALUE    - lab tests and biomarkers
  ANATOMY     - body parts / anatomical locations
  PROCEDURE   - medical procedures / treatments
"""

from typing import Dict, List, Optional
from loguru import logger

# ── Model identifier ─────────────────────────────────────────────────────────
_NER_MODEL_ID = "blaze999/Medical-NER"

# ── Module-level singletons ───────────────────────────────────────────────────
_ner_pipeline = None
_ner_available: Optional[bool] = None   # None = not yet checked


def _load_pipeline():
    """
    Lazy-load the NER pipeline on first call.

    Returns the pipeline object on success, None if the dependency or model
    is unavailable (fails gracefully — the app never crashes for missing NER).
    """
    global _ner_pipeline, _ner_available

    if _ner_available is False:          # Previously failed — skip retry
        return None
    if _ner_pipeline is not None:        # Already loaded
        return _ner_pipeline

    try:
        from transformers import pipeline  # type: ignore
        logger.info(f"[MedicalNER] Loading {_NER_MODEL_ID} ...")
        _ner_pipeline = pipeline(
            "ner",
            model=_NER_MODEL_ID,
            aggregation_strategy="simple",   # merge sub-tokens into whole words
            device=-1,                        # CPU; change to 0 for GPU
        )
        _ner_available = True
        logger.info("[MedicalNER] Pipeline loaded successfully")
    except Exception as exc:
        _ner_available = False
        logger.warning(f"[MedicalNER] Could not load NER pipeline: {exc}")
        _ner_pipeline = None

    return _ner_pipeline


# ── Entity-type display config ────────────────────────────────────────────────
_ENTITY_LABELS: Dict[str, Dict[str, str]] = {
    "DISEASE":   {"icon": "🩺", "label": "Condition / Disease"},
    "DRUG":      {"icon": "💊", "label": "Medication / Drug"},
    "SYMPTOM":   {"icon": "🤒", "label": "Symptom"},
    "LABVALUE":  {"icon": "🧪", "label": "Lab / Biomarker"},
    "ANATOMY":   {"icon": "🫀", "label": "Anatomy"},
    "PROCEDURE": {"icon": "⚕️",  "label": "Procedure / Treatment"},
}

# Minimum confidence threshold to surface an entity
_SCORE_THRESHOLD = 0.70


def extract_entities(text: str) -> List[Dict]:
    """
    Extract medical entities from *text*.

    Returns a list of dicts:
    ```
    [
      {"entity": "hypertension", "type": "DISEASE", "score": 0.97,
       "icon": "🩺", "label": "Condition / Disease"},
      ...
    ]
    ```

    Returns an empty list if the NER pipeline is unavailable or the text
    contains no entities above the confidence threshold.
    """
    if not text or not text.strip():
        return []

    pipe = _load_pipeline()
    if pipe is None:
        return []

    try:
        raw = pipe(text)
    except Exception as exc:
        logger.warning(f"[MedicalNER] Inference error: {exc}")
        return []

    entities: List[Dict] = []
    seen: set = set()                    # deduplicate by (word, type)

    for item in raw:
        score: float = float(item.get("score", 0))
        if score < _SCORE_THRESHOLD:
            continue

        word: str  = item.get("word", "").strip()
        etype: str = (item.get("entity_group") or item.get("entity", "")).upper()

        if not word or not etype:
            continue

        key = (word.lower(), etype)
        if key in seen:
            continue
        seen.add(key)

        meta = _ENTITY_LABELS.get(etype, {"icon": "🔬", "label": etype.title()})
        entities.append({
            "entity": word,
            "type":   etype,
            "score":  round(score, 3),
            "icon":   meta["icon"],
            "label":  meta["label"],
        })

    # Sort by confidence descending, cap at 10 entities
    entities.sort(key=lambda e: e["score"], reverse=True)
    return entities[:10]


def group_by_type(entities: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group a list of entity dicts by their *type* field.

    Useful for rendering grouped entity chips in the UI.
    """
    groups: Dict[str, List[Dict]] = {}
    for ent in entities:
        groups.setdefault(ent["type"], []).append(ent)
    return groups


def is_available() -> bool:
    """Return True if the NER pipeline loaded successfully."""
    if _ner_available is None:
        _load_pipeline()
    return bool(_ner_available)
