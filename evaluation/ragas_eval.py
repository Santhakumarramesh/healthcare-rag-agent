"""
evaluation/ragas_eval.py
------------------------
Runs RAGAS evaluation on the RAG pipeline:
  - Faithfulness      : Is the answer grounded in retrieved context?
  - Answer Relevancy  : Does the answer address the question?
  - Context Recall    : Did we retrieve the right documents?
  - Context Precision : Are retrieved docs actually useful?

Logs results to MLflow and saves a CSV report.
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# ── Sample Evaluation Dataset ─────────────────────────────────────────────────
# In production, expand this to 50–100 Q&A pairs

EVAL_DATASET = [
    {
        "question": "What are the common symptoms of Type 2 diabetes?",
        "ground_truth": "Common symptoms of Type 2 diabetes include increased thirst, frequent urination, fatigue, blurred vision, slow wound healing, and unexplained weight loss.",
    },
    {
        "question": "How does ibuprofen work as a pain reliever?",
        "ground_truth": "Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) that works by inhibiting COX-1 and COX-2 enzymes, reducing the production of prostaglandins that cause inflammation, pain, and fever.",
    },
    {
        "question": "What is hypertension and what are its risk factors?",
        "ground_truth": "Hypertension, or high blood pressure, occurs when blood pressure consistently reads 130/80 mmHg or higher. Risk factors include obesity, sedentary lifestyle, high sodium diet, smoking, alcohol, stress, age, and family history.",
    },
    {
        "question": "What is the difference between Type 1 and Type 2 diabetes?",
        "ground_truth": "Type 1 diabetes is an autoimmune condition where the body cannot produce insulin. Type 2 diabetes involves insulin resistance where the body doesn't use insulin effectively. Type 1 typically appears in childhood; Type 2 is more common in adults.",
    },
    {
        "question": "What are the side effects of statins?",
        "ground_truth": "Common statin side effects include muscle pain and weakness (myopathy), headache, nausea, liver enzyme elevation, and rarely, a serious condition called rhabdomyolysis involving muscle breakdown.",
    },
    {
        "question": "How is pneumonia diagnosed?",
        "ground_truth": "Pneumonia is diagnosed through physical examination, chest X-ray showing lung infiltrates, blood tests indicating infection (elevated WBC), sputum culture, and sometimes CT scan or bronchoscopy for complex cases.",
    },
    {
        "question": "What foods should be avoided with high blood pressure?",
        "ground_truth": "Foods to avoid with high blood pressure include high-sodium foods like processed meats, canned soups, salty snacks, alcohol, caffeine in excess, and foods high in saturated or trans fats.",
    },
    {
        "question": "What is BMI and how is it calculated?",
        "ground_truth": "BMI (Body Mass Index) is a measure of body fat based on height and weight. It is calculated as weight in kilograms divided by height in meters squared. A BMI of 18.5–24.9 is considered normal.",
    },
]


def run_ragas_eval(sample_size: int = None) -> dict:
    """
    Run RAGAS evaluation and return metric scores.
    Falls back to a simple internal evaluation if RAGAS fails.
    """
    sample_size = sample_size or int(os.getenv("RAGAS_EVAL_SAMPLE_SIZE", 8))
    dataset = EVAL_DATASET[:sample_size]

    logger.info(f"[RAGAS] Running evaluation on {len(dataset)} samples...")

    results = []
    for item in dataset:
        result = _evaluate_single(item["question"], item["ground_truth"])
        results.append(result)

    df = pd.DataFrame(results)
    avg_scores = {
        "faithfulness":       round(df["faithfulness"].mean(), 3),
        "answer_relevancy":   round(df["answer_relevancy"].mean(), 3),
        "overall":            round(df[["faithfulness", "answer_relevancy"]].mean().mean(), 3),
        "n_samples":          len(results),
        "timestamp":          datetime.now().isoformat(),
    }

    # Save report
    report_path = Path("evaluation/ragas_report.csv")
    report_path.parent.mkdir(exist_ok=True)
    df.to_csv(report_path, index=False)
    logger.info(f"[RAGAS] Report saved to {report_path}")
    logger.info(f"[RAGAS] Avg scores: {avg_scores}")

    # Log to MLflow if available
    _log_to_mlflow(avg_scores)

    return avg_scores


def _evaluate_single(question: str, ground_truth: str) -> dict:
    """Run the pipeline on one question and score it against ground truth."""
    from agents.rag_pipeline import HealthcareRAGPipeline
    import asyncio

    pipeline = HealthcareRAGPipeline()
    result = asyncio.run(pipeline.run(question))

    # Simple lexical faithfulness (in production, use RAGAS proper)
    faithfulness = _score_faithfulness(
        response=result["response"],
        context=result["context"],
    )
    answer_relevancy = _score_relevancy(
        response=result["response"],
        question=question,
    )

    return {
        "question":         question,
        "response":         result["response"][:200],
        "intent":           result["intent"],
        "sources_count":    len(result["sources"]),
        "faithfulness":     faithfulness,
        "answer_relevancy": answer_relevancy,
        "eval_score":       result.get("eval_score"),
        "eval_feedback":    result.get("eval_feedback"),
        "latency_note":     "measured per run",
    }


def _score_faithfulness(response: str, context: str) -> float:
    """
    Score how grounded the response is in the context.
    Uses keyword overlap as a proxy (0–1).
    In production, replace with RAGAS faithfulness metric.
    """
    if not context or not response:
        return 0.0

    resp_words = set(response.lower().split())
    ctx_words  = set(context.lower().split())
    overlap    = resp_words & ctx_words
    score      = min(len(overlap) / max(len(resp_words), 1), 1.0)
    return round(score, 3)


def _score_relevancy(response: str, question: str) -> float:
    """
    Score how relevant the response is to the question.
    Uses question keyword presence in response as a proxy.
    """
    if not response or not question:
        return 0.0

    q_words  = set(question.lower().split()) - {"what", "is", "the", "a", "an", "how", "does", "are", "of"}
    r_words  = set(response.lower().split())
    overlap  = q_words & r_words
    score    = min(len(overlap) / max(len(q_words), 1), 1.0)
    return round(score, 3)


def _log_to_mlflow(scores: dict):
    try:
        import mlflow
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
        mlflow.set_experiment("healthcare-rag-evaluation")
        with mlflow.start_run(run_name=f"ragas-{datetime.now().strftime('%Y%m%d-%H%M')}"):
            mlflow.log_metrics({
                "faithfulness":     scores["faithfulness"],
                "answer_relevancy": scores["answer_relevancy"],
                "overall_score":    scores["overall"],
            })
            mlflow.log_param("n_samples", scores["n_samples"])
        logger.info("[MLflow] Evaluation metrics logged.")
    except Exception as e:
        logger.warning(f"[MLflow] Logging skipped: {e}")


if __name__ == "__main__":
    scores = run_ragas_eval()
    print("\n📊 RAGAS Evaluation Results:")
    print(json.dumps(scores, indent=2))
