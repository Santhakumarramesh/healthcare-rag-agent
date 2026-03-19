"""
Medical Record Analysis Agent.

Two capabilities:
  1. Structured extraction — parse an uploaded record into diagnoses, labs,
     medications, abnormal flags, and a plain-language summary.
  2. Grounded QA — answer patient questions using only text from their records.
"""
import json
import sys
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.config import config


# ── LLM factory ───────────────────────────────────────────────────────────────

def _llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=temperature,
    )


# ── Prompts ───────────────────────────────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """You are an expert medical record analyst trained to extract structured data from ANY format of medical document, including:
- Lab reports (blood tests, urinalysis, radiology, pathology)
- Discharge summaries
- Doctor's notes and prescriptions
- Hospital records
- Imaging reports (X-ray, CT, MRI, ultrasound)
- Vaccination records

You must be EXTREMELY CAREFUL to extract the ACTUAL patient information from the document, not placeholder or example data.

Return ONLY valid JSON with this exact schema (no markdown fences, no extra text):
{
  "patient_info": {
    "name": "<ACTUAL full name from document or 'Not specified'>",
    "dob": "<ACTUAL date of birth or age or 'Not specified'>",
    "record_date": "<ACTUAL date of this record or 'Not specified'>",
    "provider": "<ACTUAL doctor/clinic/hospital name or 'Not specified'>"
  },
  "diagnoses": ["<diagnosis 1>", "<diagnosis 2>"],
  "medications": [
    {"name": "<drug>", "dose": "<dose>", "frequency": "<how often>", "indication": "<what it treats>"}
  ],
  "lab_values": [
    {
      "name": "<EXACT test name as written>",
      "value": "<EXACT result with unit>",
      "normal_range": "<reference range if provided, or 'N/A'>",
      "status": "<NORMAL|HIGH|LOW|CRITICAL|UNKNOWN>",
      "interpretation": "<one plain-English sentence explaining what this means>"
    }
  ],
  "abnormal_flags": ["<brief description of each abnormal or critical finding>"],
  "allergies": ["<allergy 1>"],
  "key_findings": "<2-3 sentence plain-English summary of the most important findings>",
  "recommended_actions": ["<action the patient should discuss with their doctor>"]
}

CRITICAL RULES:
1. Extract the REAL patient name, date, and provider from the document - DO NOT use placeholder names like "John Smith" or "Jane Doe"
2. If you see table data, parse it carefully - lab values are often in tables with columns like: Test Name | Result | Reference Range | Units
3. For lab status: 
   - HIGH = result above reference range upper limit
   - LOW = result below reference range lower limit  
   - CRITICAL = dangerously out of range (typically marked with flags like *, H, L, or CRITICAL)
   - NORMAL = within reference range
   - UNKNOWN = no reference range provided
4. Include ALL lab values found, even normal ones
5. Look for dates in various formats: DD/MM/YYYY, MM/DD/YYYY, DD-MMM-YYYY, etc.
6. Look for patient identifiers: MRN, Patient ID, Registration Number
7. Extract ALL medications mentioned, including dosage and frequency
8. If the document is an imaging report (X-ray, CT, MRI), put findings in "diagnoses" and key observations in "key_findings"
9. Do NOT diagnose, prescribe, or speculate beyond what the record explicitly states
10. Respond ONLY with the JSON object - no explanations, no markdown fences"""


RECORDS_QA_SYSTEM_PROMPT = """You are a Medical Records Assistant helping a patient understand their own uploaded health records.

You will be given excerpts retrieved from the patient's documents. Answer their question based STRICTLY on those excerpts.

Rules:
1. Use ONLY information from the provided excerpts — never use outside knowledge to fill gaps.
2. If the answer isn't in the excerpts, say: "I don't see that in the records you uploaded."
3. Never diagnose, prescribe, or recommend treatments.
4. Explain medical jargon in plain English.
5. If a lab value is abnormal, explain what high/low means in plain language — do NOT speculate on cause.
6. Always end with the disclaimer below.

End EVERY response with:
"⚕️ Remember: This is based only on the records you uploaded. Always discuss your results with your healthcare provider.\""""


# ── Agent functions ────────────────────────────────────────────────────────────

async def extract_record_structure(full_text: str) -> dict:
    """
    Parse all uploaded record text and return a structured JSON dict.
    Truncated to ~12 000 chars to stay within GPT-4o-mini's context window
    while still covering most single-page lab reports and discharge summaries.
    """
    llm = _llm(temperature=0.0)
    text_to_send = full_text[:12_000] if len(full_text) > 12_000 else full_text

    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(content=f"Medical record text:\n\n{text_to_send}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Defensively strip markdown fences if the model adds them anyway
        if content.startswith("```"):
            parts = content.split("```")
            content = parts[1].lstrip("json").strip() if len(parts) > 1 else content

        result = json.loads(content)
        logger.info("[RecordsAgent] Structured extraction complete.")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"[RecordsAgent] JSON parse error: {e}\nRaw: {content[:200]}")
        return {
            "error": "Could not parse extraction result.",
            "key_findings": "Extraction failed. Try asking specific questions below.",
            "diagnoses": [], "medications": [], "lab_values": [],
            "abnormal_flags": [], "allergies": [], "recommended_actions": [],
            "patient_info": {}, "raw_response": content[:500],
        }
    except Exception as e:
        logger.error(f"[RecordsAgent] Extraction failed: {e}")
        return {
            "error": str(e),
            "key_findings": "An error occurred during extraction. Try asking specific questions below.",
            "diagnoses": [], "medications": [], "lab_values": [],
            "abnormal_flags": [], "allergies": [], "recommended_actions": [],
            "patient_info": {},
        }


async def answer_record_question(question: str, context_chunks: list) -> str:
    """Answer a patient question grounded in retrieved chunks from their records."""
    llm = _llm(temperature=0.1)

    if not context_chunks:
        return (
            "I couldn't find relevant information in your uploaded records for that question. "
            "Try rephrasing, or make sure the relevant document has been uploaded.\n\n"
            "⚕️ Remember: This is based only on the records you uploaded. Always discuss your "
            "results with your healthcare provider."
        )

    context_parts = []
    for chunk in context_chunks:
        source = chunk.metadata.get("source", "uploaded record")
        context_parts.append(f"[From: {source}]\n{chunk.text}")
    context = "\n\n---\n\n".join(context_parts)

    messages = [
        SystemMessage(content=RECORDS_QA_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"EXCERPTS FROM PATIENT'S RECORDS:\n{context}\n\n"
            f"PATIENT'S QUESTION: {question}"
        )),
    ]

    try:
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"[RecordsAgent] QA failed: {e}")
        return (
            f"Sorry, I encountered an error while answering your question: {e}\n\n"
            "⚕️ Always discuss your results with your healthcare provider."
        )
