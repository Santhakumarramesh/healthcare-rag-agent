"""
data/download_datasets.py
--------------------------
Downloads free healthcare datasets from HuggingFace, converts them to
RAG-ready text chunks, and ingests into the FAISS vector store.

Improvements applied:
  Fix 1 — Dependency check at module top (crashes with helpful message, not ImportError)
  Fix 2 — Resumable: skips already-downloaded/processed files
  Fix 3 — Retry logic: exponential backoff on network failures (tenacity)
  Fix 4 — Memory-efficient: uses ds.to_csv() instead of ds.to_pandas()
  Fix 5 — Configurable limits: constants at top + CLI --max-* args
  Fix 6 — Strict column validation: raises ValueError on schema drift, never falls back silently

Usage:
    python data/download_datasets.py                       # default limits
    python data/download_datasets.py --max-medquad 5000   # smaller run
    python data/download_datasets.py --force               # re-download everything
    python data/download_datasets.py --skip-ingest         # download only, no FAISS
"""

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: Dependency guard — runs BEFORE any other import so the user
#         gets a helpful message instead of a raw ImportError traceback.
# ─────────────────────────────────────────────────────────────────────────────
import sys

_REQUIRED = [
    ("datasets",      "datasets"),
    ("pandas",        "pandas"),
    ("loguru",        "loguru"),
    ("python-dotenv", "dotenv"),
    ("tenacity",      "tenacity"),
]

_MISSING = []
for _pip_name, _import_name in _REQUIRED:
    try:
        __import__(_import_name)
    except ImportError:
        _MISSING.append(_pip_name)

if _MISSING:
    print("\n❌  Missing dependencies. Run:\n")
    print(f"    pip install {' '.join(_MISSING)}\n")
    print("Or install everything:\n")
    print("    pip install -r requirements.txt\n")
    sys.exit(1)

# ── Safe imports ───────────────────────────────────────────────────────────────
import os
import argparse
from pathlib import Path

import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# FIX 5: Sample limits as named top-level constants.
#         Readable, easy to change, and overridable via env vars or CLI.
# ─────────────────────────────────────────────────────────────────────────────
MAX_MEDQUAD_SAMPLES    = int(os.getenv("MAX_MEDQUAD_SAMPLES",    10_000))
MAX_MEDMCQA_SAMPLES    = int(os.getenv("MAX_MEDMCQA_SAMPLES",    15_000))
MAX_CHATDOCTOR_SAMPLES = int(os.getenv("MAX_CHATDOCTOR_SAMPLES", 10_000))
MAX_MEDDATASET_SAMPLES = int(os.getenv("MAX_MEDDATASET_SAMPLES",  5_000))

OUTPUT_DIR    = Path(__file__).parent / "raw_datasets"
PROCESSED_DIR = Path(__file__).parent / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# FIX 3: Retry decorator for all HuggingFace network calls.
#         Retries up to 3×, doubling the wait each time (4s → 8s → 16s).
# ─────────────────────────────────────────────────────────────────────────────
def hf_retry(fn):
    """Wrap a function with exponential-backoff retry for transient network errors."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
        before_sleep=lambda rs: logger.warning(
            f"  ⚠️  Network blip — retrying in {rs.next_action.sleep:.0f}s "
            f"(attempt {rs.attempt_number}/3)..."
        ),
    )(fn)


# ─────────────────────────────────────────────────────────────────────────────
# FIX 6: Strict column resolver.
#         Checks a priority list of known column names. If none match,
#         raises a clear ValueError rather than silently falling back to
#         df.columns[0], which could be an ID, a URL, or garbage.
# ─────────────────────────────────────────────────────────────────────────────

# Known valid column names for each dataset × role.
# Update these lists if HuggingFace renames columns in a schema update.
KNOWN_SCHEMAS: dict[str, dict[str, list[str]]] = {
    "medquad": {
        "question": ["Question", "question", "QUESTION"],
        "answer":   ["Answer",   "answer",   "ANSWER"],
    },
    "medmcqa": {
        "question": ["question"],
        # correct_answer is a derived column added after download
        "answer":   ["correct_answer"],
        "exp":      ["exp"],
    },
    "chatdoctor": {
        "question": ["input",   "question", "patient", "Patient"],
        "answer":   ["output",  "answer",   "doctor",  "Doctor"],
    },
    "med_dataset": {
        "question": ["question", "Question", "input",    "instruction"],
        "answer":   ["answer",   "Answer",   "output",   "response"],
    },
}


def resolve_column(df: pd.DataFrame, candidates: list[str], dataset: str, role: str) -> str:
    """
    Return the first column name from `candidates` that exists in `df`.
    Raises ValueError (never silently falls back) if none are found.
    """
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(
        f"\n[{dataset}] Cannot find '{role}' column.\n"
        f"  Expected one of : {candidates}\n"
        f"  Actual columns  : {list(df.columns)}\n"
        f"  → The dataset schema on HuggingFace may have changed.\n"
        f"    Update KNOWN_SCHEMAS['{dataset}']['{role}'] in download_datasets.py."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Downloaders
# ─────────────────────────────────────────────────────────────────────────────

@hf_retry
def _fetch_medquad():
    from datasets import load_dataset
    return load_dataset("keivalya/MedQuad-MedicalQnADataset", split="train")


def download_medquad(force: bool = False) -> Path | None:
    """47,457 NIH Q&A pairs. License: CC BY 4.0"""
    out = OUTPUT_DIR / "medquad.csv"

    # FIX 2: Skip if already on disk
    if out.exists() and not force:
        logger.info(f"⏭️  MedQuAD already downloaded ({out.stat().st_size // 1024} KB) — skipping.")
        return out

    logger.info("📥 Downloading MedQuAD …")
    try:
        ds = _fetch_medquad()
        ds.to_csv(str(out))          # FIX 4: no .to_pandas() memory spike
        logger.info(f"✅ MedQuAD → {out}  ({len(ds):,} rows)")
        return out
    except Exception as e:
        logger.error(f"❌ MedQuAD failed: {e}")
        return None


@hf_retry
def _fetch_medmcqa():
    from datasets import load_dataset
    return load_dataset("openlifescienceai/medmcqa", split="train")


def download_medmcqa(force: bool = False) -> Path | None:
    """194k medical exam Q&A. License: MIT"""
    out = OUTPUT_DIR / "medmcqa.csv"

    if out.exists() and not force:
        logger.info(f"⏭️  MedMCQA already downloaded ({out.stat().st_size // 1024} KB) — skipping.")
        return out

    logger.info("📥 Downloading MedMCQA …")
    try:
        ds = _fetch_medmcqa()

        # FIX 4: select only needed columns before export
        needed = ["question", "exp", "cop", "opa", "opb", "opc", "opd"]
        ds = ds.select_columns([c for c in needed if c in ds.column_names])

        # Derive correct_answer in-place (avoids full pandas conversion)
        option_map = {0: "opa", 1: "opb", 2: "opc", 3: "opd"}
        ds = ds.map(
            lambda row: {**row, "correct_answer": row.get(option_map.get(row.get("cop", 0), "opa"), "")},
            desc="Mapping correct answers",
        )
        ds.to_csv(str(out))
        logger.info(f"✅ MedMCQA → {out}  ({len(ds):,} rows)")
        return out
    except Exception as e:
        logger.error(f"❌ MedMCQA failed: {e}")
        return None


@hf_retry
def _fetch_chatdoctor():
    from datasets import load_dataset
    return load_dataset("avaliev/chat_doctor", split="train")


def download_chatdoctor(force: bool = False) -> Path | None:
    """110k patient-doctor dialogues. License: CC BY NC 4.0"""
    out = OUTPUT_DIR / "chatdoctor.csv"

    if out.exists() and not force:
        logger.info(f"⏭️  ChatDoctor already downloaded ({out.stat().st_size // 1024} KB) — skipping.")
        return out

    logger.info("📥 Downloading ChatDoctor …")
    try:
        ds = _fetch_chatdoctor()
        ds.to_csv(str(out))
        logger.info(f"✅ ChatDoctor → {out}  ({len(ds):,} rows)")
        return out
    except Exception as e:
        logger.warning(f"⚠️  ChatDoctor unavailable: {e}")
        return None


@hf_retry
def _fetch_med_dataset():
    from datasets import load_dataset
    return load_dataset("Med-dataset/Med_Dataset", split="test")


def download_med_dataset(force: bool = False) -> Path | None:
    """5k curated medical instruction pairs."""
    out = OUTPUT_DIR / "med_dataset.csv"

    if out.exists() and not force:
        logger.info(f"⏭️  Med_Dataset already downloaded ({out.stat().st_size // 1024} KB) — skipping.")
        return out

    logger.info("📥 Downloading Med_Dataset …")
    try:
        ds = _fetch_med_dataset()
        ds.to_csv(str(out))
        logger.info(f"✅ Med_Dataset → {out}  ({len(ds):,} rows)")
        return out
    except Exception as e:
        logger.error(f"❌ Med_Dataset failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Converters — CSV → RAG-ready plain text
# ─────────────────────────────────────────────────────────────────────────────

def convert_medquad(csv_path: Path, max_samples: int) -> Path | None:
    out = PROCESSED_DIR / "medquad_rag.txt"
    if out.exists() and out.stat().st_size > 0:
        logger.info("⏭️  medquad_rag.txt exists — skipping conversion.")
        return out

    logger.info(f"🔄 Converting MedQuAD (max {max_samples:,}) …")
    df = pd.read_csv(csv_path)

    try:
        q_col = resolve_column(df, KNOWN_SCHEMAS["medquad"]["question"], "medquad", "question")
        a_col = resolve_column(df, KNOWN_SCHEMAS["medquad"]["answer"],   "medquad", "answer")
    except ValueError as e:
        logger.error(str(e))
        return None

    lines = []
    for _, row in df.iterrows():
        q, a = str(row[q_col]).strip(), str(row[a_col]).strip()
        if q and a and len(a) > 20 and a.lower() not in ("nan", "none"):
            lines.append(f"Q: {q}\nA: {a}")
        if len(lines) >= max_samples:
            break

    out.write_text("\n---\n".join(lines), encoding="utf-8")
    logger.info(f"✅ medquad_rag.txt → {len(lines):,} pairs")
    return out


def convert_medmcqa(csv_path: Path, max_samples: int) -> Path | None:
    out = PROCESSED_DIR / "medmcqa_rag.txt"
    if out.exists() and out.stat().st_size > 0:
        logger.info("⏭️  medmcqa_rag.txt exists — skipping conversion.")
        return out

    logger.info(f"🔄 Converting MedMCQA (max {max_samples:,}) …")
    df = pd.read_csv(csv_path)

    try:
        q_col = resolve_column(df, KNOWN_SCHEMAS["medmcqa"]["question"], "medmcqa", "question")
        a_col = resolve_column(df, KNOWN_SCHEMAS["medmcqa"]["answer"],   "medmcqa", "answer")
    except ValueError as e:
        logger.error(str(e))
        return None

    exp_col = "exp" if "exp" in df.columns else None
    lines = []
    for _, row in df.iterrows():
        q, a = str(row[q_col]).strip(), str(row[a_col]).strip()
        if q and a and a.lower() not in ("nan", "none"):
            entry = f"Q: {q}\nA: {a}"
            if exp_col:
                exp = str(row[exp_col]).strip()
                if exp and exp.lower() not in ("nan", "none") and len(exp) > 10:
                    entry += f"\nExplanation: {exp}"
            lines.append(entry)
        if len(lines) >= max_samples:
            break

    out.write_text("\n---\n".join(lines), encoding="utf-8")
    logger.info(f"✅ medmcqa_rag.txt → {len(lines):,} pairs")
    return out


def convert_chatdoctor(csv_path: Path, max_samples: int) -> Path | None:
    out = PROCESSED_DIR / "chatdoctor_rag.txt"
    if out.exists() and out.stat().st_size > 0:
        logger.info("⏭️  chatdoctor_rag.txt exists — skipping conversion.")
        return out

    logger.info(f"🔄 Converting ChatDoctor (max {max_samples:,}) …")
    df = pd.read_csv(csv_path)

    try:
        q_col = resolve_column(df, KNOWN_SCHEMAS["chatdoctor"]["question"], "chatdoctor", "question")
        a_col = resolve_column(df, KNOWN_SCHEMAS["chatdoctor"]["answer"],   "chatdoctor", "answer")
    except ValueError as e:
        logger.error(str(e))
        return None

    lines = []
    for _, row in df.iterrows():
        q, a = str(row[q_col]).strip(), str(row[a_col]).strip()
        if q and a and len(a) > 20 and a.lower() not in ("nan", "none"):
            lines.append(f"Patient: {q}\nDoctor: {a}")
        if len(lines) >= max_samples:
            break

    out.write_text("\n---\n".join(lines), encoding="utf-8")
    logger.info(f"✅ chatdoctor_rag.txt → {len(lines):,} pairs")
    return out


def convert_med_dataset(csv_path: Path, max_samples: int) -> Path | None:
    out = PROCESSED_DIR / "med_dataset_rag.txt"
    if out.exists() and out.stat().st_size > 0:
        logger.info("⏭️  med_dataset_rag.txt exists — skipping conversion.")
        return out

    logger.info(f"🔄 Converting Med_Dataset (max {max_samples:,}) …")
    df = pd.read_csv(csv_path)

    try:
        q_col = resolve_column(df, KNOWN_SCHEMAS["med_dataset"]["question"], "med_dataset", "question")
        a_col = resolve_column(df, KNOWN_SCHEMAS["med_dataset"]["answer"],   "med_dataset", "answer")
    except ValueError as e:
        logger.error(str(e))
        return None

    lines = []
    for _, row in df.iterrows():
        q, a = str(row[q_col]).strip(), str(row[a_col]).strip()
        if q and a and len(a) > 20 and a.lower() not in ("nan", "none"):
            lines.append(f"Q: {q}\nA: {a}")
        if len(lines) >= max_samples:
            break

    out.write_text("\n---\n".join(lines), encoding="utf-8")
    logger.info(f"✅ med_dataset_rag.txt → {len(lines):,} pairs")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Vector Store Ingestion
# ─────────────────────────────────────────────────────────────────────────────

def ingest_all(text_files: list[Path]) -> int:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.vector_store import HybridVectorStore
    vs = HybridVectorStore()

    total = 0
    for path in text_files:
        if path and path.exists():
            size_kb = path.stat().st_size // 1024
            logger.info(f"  Ingesting {path.name} ({size_kb} KB) …")
            chunks = vs.ingest_documents(str(path))
            total += chunks
            logger.info(f"  → {chunks:,} chunks added")

    kb = Path(__file__).parent / "healthcare_knowledge_base.md"
    if kb.exists():
        chunks = vs.ingest_documents(str(kb))
        total += chunks
        logger.info(f"  → {chunks:,} chunks from curated knowledge base")

    logger.info(f"\n  Vector store total: {vs.get_stats().get('faiss_vectors', total):,} vectors")
    return total


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Download & ingest healthcare datasets")
    p.add_argument("--force",           action="store_true",
                   help="Re-download and re-process even if files already exist")
    p.add_argument("--skip-ingest",     action="store_true",
                   help="Skip FAISS ingestion (download + convert only)")
    p.add_argument("--max-medquad",     type=int, default=MAX_MEDQUAD_SAMPLES,
                   metavar="N", help=f"MedQuAD sample limit (default {MAX_MEDQUAD_SAMPLES:,})")
    p.add_argument("--max-medmcqa",     type=int, default=MAX_MEDMCQA_SAMPLES,
                   metavar="N", help=f"MedMCQA sample limit (default {MAX_MEDMCQA_SAMPLES:,})")
    p.add_argument("--max-chatdoctor",  type=int, default=MAX_CHATDOCTOR_SAMPLES,
                   metavar="N", help=f"ChatDoctor sample limit (default {MAX_CHATDOCTOR_SAMPLES:,})")
    p.add_argument("--max-med-dataset", type=int, default=MAX_MEDDATASET_SAMPLES,
                   metavar="N", help=f"Med_Dataset sample limit (default {MAX_MEDDATASET_SAMPLES:,})")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    logger.info("=" * 70)
    logger.info("🏥 Healthcare RAG — Dataset Pipeline")
    logger.info(f"   Limits  MedQuAD:{args.max_medquad:,}  MedMCQA:{args.max_medmcqa:,}  "
                f"ChatDoctor:{args.max_chatdoctor:,}  Med_Dataset:{args.max_med_dataset:,}")
    logger.info(f"   Force:{args.force}  SkipIngest:{args.skip_ingest}")
    logger.info("=" * 70)

    # ── 1. Download ─────────────────────────────────────────────────────────
    logger.info("\n📥 STEP 1 — Download\n")
    csvs = {
        "medquad":     download_medquad(args.force),
        "medmcqa":     download_medmcqa(args.force),
        "chatdoctor":  download_chatdoctor(args.force),
        "med_dataset": download_med_dataset(args.force),
    }

    # ── 2. Convert ──────────────────────────────────────────────────────────
    logger.info("\n🔄 STEP 2 — Convert to RAG text\n")
    processed: list[Path] = []

    converters = [
        (csvs["medquad"],     convert_medquad,     args.max_medquad),
        (csvs["medmcqa"],     convert_medmcqa,     args.max_medmcqa),
        (csvs["chatdoctor"],  convert_chatdoctor,  args.max_chatdoctor),
        (csvs["med_dataset"], convert_med_dataset, args.max_med_dataset),
    ]
    for csv_path, converter, limit in converters:
        if csv_path:
            result = converter(csv_path, limit)
            if result:
                processed.append(result)

    # ── 3. Ingest ───────────────────────────────────────────────────────────
    if not args.skip_ingest:
        logger.info("\n🧠 STEP 3 — Ingest into FAISS\n")
        total = ingest_all(processed)
    else:
        logger.info("\n⏭️  Skipping ingestion (--skip-ingest).")
        total = 0

    # ── Summary ─────────────────────────────────────────────────────────────
    ok  = sum(1 for v in csvs.values() if v)
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ Done!  {ok}/{len(csvs)} datasets · {len(processed)} text files · {total:,} vectors")
    logger.info("   Run: python run.py api  →  python run.py ui")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
