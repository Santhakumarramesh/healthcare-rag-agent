"""
Multi-Step Reasoning Agent - Performs structured reasoning for complex queries.

Breaks down complex medical queries into steps:
1. Problem understanding
2. Evidence gathering
3. Condition comparison
4. Answer generation
5. Validation
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


class ReasoningAgent:
    """
    Performs multi-step reasoning for complex medical queries.
    
    Steps:
    1. Analyze problem
    2. Organize evidence
    3. Compare conditions
    4. Generate answer
    5. Validate answer
    """
    
    PROBLEM_ANALYSIS_PROMPT = """You are a medical problem analyzer. Break down this query into key components.

Identify:
1. Main medical concern
2. Relevant symptoms/conditions mentioned
3. What the user wants to know
4. Any context or constraints

Return a structured analysis in 2-3 sentences."""

    EVIDENCE_ORGANIZATION_PROMPT = """You are organizing medical evidence. Given these retrieved documents, organize them by relevance and topic.

Group evidence into:
1. Directly relevant (answers the question)
2. Supporting information (provides context)
3. Related but tangential

Summarize each group in 1-2 sentences."""

    CONDITION_COMPARISON_PROMPT = """You are comparing medical conditions or treatments. Given the evidence, compare the relevant options.

For each option:
1. Key characteristics
2. Pros/cons or benefits/risks
3. When it's appropriate
4. Evidence strength

Be objective and evidence-based."""

    ANSWER_GENERATION_PROMPT = """You are generating a final medical answer. Based on the reasoning steps, provide a clear, accurate answer.

Structure:
1. Direct answer to the question
2. Key supporting points (2-3)
3. Important caveats or warnings
4. When to seek professional help

Use simple language. Be accurate and helpful."""

    VALIDATION_PROMPT = """You are validating a medical answer. Check if the answer:

1. Answers the original question
2. Is grounded in the provided evidence
3. Contains appropriate medical disclaimers
4. Is clear and understandable
5. Doesn't make claims beyond the evidence

Return: "VALID" or "NEEDS_REVISION" with brief reason."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.1
        )
        logger.info("[ReasoningAgent] Initialized")
    
    async def reason(
        self,
        query: str,
        evidence: List[str],
        context: Optional[str] = None
    ) -> Dict:
        """
        Perform multi-step reasoning.
        
        Args:
            query: User's question
            evidence: Retrieved evidence/documents
            context: Optional conversation context
        
        Returns:
            Dict with reasoning steps and final answer
        """
        reasoning_steps = []
        
        try:
            # Step 1: Analyze Problem
            problem_analysis = await self._analyze_problem(query, context)
            reasoning_steps.append({
                "step": 1,
                "name": "Problem Analysis",
                "output": problem_analysis
            })
            
            # Step 2: Organize Evidence
            organized_evidence = await self._organize_evidence(query, evidence)
            reasoning_steps.append({
                "step": 2,
                "name": "Evidence Organization",
                "output": organized_evidence
            })
            
            # Step 3: Compare Conditions (if applicable)
            comparison = await self._compare_conditions(query, organized_evidence)
            reasoning_steps.append({
                "step": 3,
                "name": "Condition Comparison",
                "output": comparison
            })
            
            # Step 4: Generate Answer
            answer = await self._generate_answer(query, reasoning_steps)
            reasoning_steps.append({
                "step": 4,
                "name": "Answer Generation",
                "output": answer
            })
            
            # Step 5: Validate Answer
            validation = await self._validate_answer(query, answer, evidence)
            reasoning_steps.append({
                "step": 5,
                "name": "Validation",
                "output": validation
            })
            
            # Calculate confidence based on validation
            confidence = 0.9 if "VALID" in validation else 0.6
            
            logger.info(f"[ReasoningAgent] Completed 5-step reasoning with confidence {confidence}")
            
            return {
                "answer": answer,
                "reasoning_steps": reasoning_steps,
                "confidence": confidence,
                "validation_status": "VALID" if "VALID" in validation else "NEEDS_REVIEW"
            }
            
        except Exception as e:
            logger.error(f"[ReasoningAgent] Reasoning failed: {e}")
            return {
                "answer": "I encountered an error during reasoning. Please try rephrasing your question.",
                "reasoning_steps": reasoning_steps,
                "confidence": 0.3,
                "validation_status": "ERROR",
                "error": str(e)
            }
    
    async def _analyze_problem(self, query: str, context: Optional[str]) -> str:
        """Step 1: Analyze the problem"""
        messages = [
            SystemMessage(content=self.PROBLEM_ANALYSIS_PROMPT),
            HumanMessage(content=f"Query: {query}\n\nContext: {context or 'None'}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def _organize_evidence(self, query: str, evidence: List[str]) -> str:
        """Step 2: Organize evidence"""
        evidence_text = "\n\n---\n\n".join(evidence[:10]) if evidence else "No evidence provided"
        
        messages = [
            SystemMessage(content=self.EVIDENCE_ORGANIZATION_PROMPT),
            HumanMessage(content=f"Query: {query}\n\nEvidence:\n{evidence_text}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def _compare_conditions(self, query: str, organized_evidence: str) -> str:
        """Step 3: Compare conditions/options"""
        messages = [
            SystemMessage(content=self.CONDITION_COMPARISON_PROMPT),
            HumanMessage(content=f"Query: {query}\n\nOrganized Evidence:\n{organized_evidence}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def _generate_answer(self, query: str, reasoning_steps: List[Dict]) -> str:
        """Step 4: Generate final answer"""
        # Combine all reasoning steps
        reasoning_summary = "\n\n".join([
            f"Step {step['step']} - {step['name']}:\n{step['output']}"
            for step in reasoning_steps
        ])
        
        messages = [
            SystemMessage(content=self.ANSWER_GENERATION_PROMPT),
            HumanMessage(content=f"Original Query: {query}\n\nReasoning Steps:\n{reasoning_summary}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def _validate_answer(self, query: str, answer: str, evidence: List[str]) -> str:
        """Step 5: Validate the answer"""
        evidence_text = "\n".join(evidence[:5]) if evidence else "No evidence"
        
        messages = [
            SystemMessage(content=self.VALIDATION_PROMPT),
            HumanMessage(content=f"Query: {query}\n\nAnswer: {answer}\n\nEvidence: {evidence_text}")
        ]
        response = await self.llm.ainvoke(messages)
        return response.content.strip()


# Singleton instance
reasoning_agent = ReasoningAgent()
