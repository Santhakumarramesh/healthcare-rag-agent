"""
RAGAS-based evaluation pipeline for the Healthcare RAG system.
Evaluates: Faithfulness, Answer Relevancy, Context Recall, Context Precision.

Run: python evaluation/evaluate.py
"""
import sys
import json
from pathlib import Path

import pandas as pd
from loguru import logger
from datasets import Dataset

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config

# Test questions for evaluation
EVAL_QUESTIONS = [
    {
        "question": "What are common symptoms of Type 2 Diabetes?",
        "ground_truth": (
            "Common symptoms of Type 2 Diabetes include increased thirst, frequent urination, "
            "unexplained weight loss, fatigue, blurred vision, slow-healing sores, and tingling "
            "in hands or feet."
        ),
    },
    {
        "question": "What is Metformin used for?",
        "ground_truth": (
            "Metformin is a first-line oral medication used to treat Type 2 Diabetes. "
            "It reduces glucose production in the liver and improves insulin sensitivity."
        ),
    },
    {
        "question": "How often should adults get a physical examination?",
        "ground_truth": (
            "Adults aged 18-39 should get a physical exam every 2-3 years, "
            "ages 40-49 every 1-2 years, and ages 50+ annually."
        ),
    },
    {
        "question": "What are warning signs of a heart attack?",
        "ground_truth": (
            "Heart attack warning signs include chest pain or pressure, pain radiating to the arm or jaw, "
            "shortness of breath, cold sweat, and nausea. Women may experience atypical symptoms."
        ),
    },
    {
        "question": "What vaccines are recommended for adults?",
        "ground_truth": (
            "Key adult vaccines include annual flu shot, COVID-19 boosters, Tdap every 10 years, "
            "Shingrix for adults 50+, pneumococcal vaccine for adults 65+, and Hepatitis A and B."
        ),
    },
]


def run_evaluation():
    """Run RAGAS evaluation on the Healthcare RAG pipeline."""
    logger.info("Starting RAGAS evaluation...")

    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        )
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    except ImportError as e:
        logger.error(f"Missing dependency: {e}. Run: pip install ragas")
        return

    from agents.rag_pipeline import HealthcareRAGPipeline
    from vectorstore.retriever import HybridRetriever

    pipeline = HealthcareRAGPipeline()
    retriever = HybridRetriever()

    # Collect evaluation data
    eval_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    logger.info(f"Running {len(EVAL_QUESTIONS)} evaluation questions...")
    for i, item in enumerate(EVAL_QUESTIONS, 1):
        logger.info(f"[{i}/{len(EVAL_QUESTIONS)}] Evaluating: '{item['question'][:50]}...'")

        result = pipeline.run(item["question"])
        chunks = retriever.retrieve(item["question"])
        contexts = [c.text for c in chunks]

        eval_data["question"].append(item["question"])
        eval_data["answer"].append(result["response"])
        eval_data["contexts"].append(contexts)
        eval_data["ground_truth"].append(item["ground_truth"])

        pipeline.reset_conversation()

    dataset = Dataset.from_dict(eval_data)

    logger.info("Running RAGAS metrics...")
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
    embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)

    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
        llm=llm,
        embeddings=embeddings,
    )

    # Display results
    results_df = results.to_pandas()
    logger.success("RAGAS Evaluation Complete!")
    logger.info("\n" + results_df[["question", "faithfulness", "answer_relevancy",
                                   "context_recall", "context_precision"]].to_string())

    # Summary
    summary = {
        "faithfulness": float(results_df["faithfulness"].mean()),
        "answer_relevancy": float(results_df["answer_relevancy"].mean()),
        "context_recall": float(results_df["context_recall"].mean()),
        "context_precision": float(results_df["context_precision"].mean()),
    }

    print("\n" + "="*60)
    print("RAGAS EVALUATION SUMMARY")
    print("="*60)
    for metric, score in summary.items():
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f"{metric:25s} [{bar}] {score:.3f}")
    print("="*60)

    # Save results
    output_path = Path("evaluation/ragas_results.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"summary": summary, "per_question": results_df.to_dict(orient="records")}, f, indent=2)
    logger.success(f"Results saved to {output_path}")

    return summary


if __name__ == "__main__":
    run_evaluation()
