"""
Hallucination detection for RAG responses.
Implements LLM-based detection approach from AWS blog.
"""
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger
import json


HALLUCINATION_DETECTION_PROMPT = """You are an expert assistant helping to check if statements are based on the context.
Your task is to read context and statement and indicate which sentences in the statement are based directly on the context.

Provide response as a number, where the number represents a hallucination score, which is a float between 0 and 1.
Set the float to 0 if you are confident that the sentence is directly based on the context.
Set the float to 1 if you are confident that the sentence is not based on the context.
If you are not confident, set the score to a float number between 0 and 1. Higher numbers represent higher confidence that the sentence is not based on the context.

Do not include any other information except for the score in the response. There is no need to explain your thinking.

Examples:

Context: Diabetes is a chronic metabolic disease characterized by elevated blood glucose levels. It occurs when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces.
Statement: 'Diabetes is a condition where blood sugar levels are too high.'
Assistant: 0.05

Context: Diabetes is a chronic metabolic disease characterized by elevated blood glucose levels. It occurs when the pancreas does not produce enough insulin or when the body cannot effectively use the insulin it produces.
Statement: 'Diabetes affects approximately 50 million people in the United States.'
Assistant: 1.0

Context: Type 2 diabetes is the most common form, accounting for about 90-95% of all diabetes cases. Risk factors include obesity, physical inactivity, and family history.
Statement: 'Type 2 diabetes is usually caused by eating too much sugar.'
Assistant: 0.85

Now evaluate:

Context: {context}
Statement: {statement}
"""


async def detect_hallucination(context: str, response: str, api_key: str) -> Dict[str, float]:
    """
    Detect hallucinations in RAG response using LLM-based scoring.
    
    Args:
        context: Retrieved context used to generate response
        response: Generated response to evaluate
        api_key: OpenAI API key
        
    Returns:
        Dict with 'score' (0-1, higher = more likely hallucinated) and 'risk_level'
    """
    if not context or not response:
        return {"score": 0.0, "risk_level": "unknown"}
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=api_key,
        )
        
        prompt = HALLUCINATION_DETECTION_PROMPT.format(
            context=context[:2000],  # Limit context to avoid token limits
            statement=response[:1000],  # Limit response
        )
        
        messages = [
            SystemMessage(content="You are a hallucination detection expert."),
            HumanMessage(content=prompt)
        ]
        
        result = await llm.ainvoke(messages)
        score_text = result.content.strip()
        
        # Parse score
        try:
            score = float(score_text)
            score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except ValueError:
            logger.warning(f"Could not parse hallucination score: {score_text}")
            score = 0.5  # Default to medium risk
        
        # Determine risk level
        if score < 0.3:
            risk_level = "low"
        elif score < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        logger.info(f"Hallucination detection: score={score:.2f}, risk={risk_level}")
        
        return {
            "score": round(score, 3),
            "risk_level": risk_level,
        }
        
    except Exception as e:
        logger.error(f"Hallucination detection failed: {e}")
        return {"score": 0.0, "risk_level": "unknown"}
