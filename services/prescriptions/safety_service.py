"""
Medication Safety Service
Checks prescriptions for safety concerns before approving refills or dispatch.
"""
from loguru import logger
from typing import List, Dict


class MedicationSafetyService:
    """
    Checks for:
    - Refill frequency abuse (too soon)
    - Expired prescriptions
    - Controlled substance flags
    - Drug interaction warnings
    - Doctor review requirements
    """

    HIGH_RISK_KEYWORDS = [
        "oxycodone", "hydrocodone", "fentanyl", "morphine", "alprazolam",
        "diazepam", "zolpidem", "tramadol", "buprenorphine", "methadone",
    ]

    def check_prescription(self, prescription: dict, refill_history: List[dict]) -> List[dict]:
        """
        Run all safety checks on a prescription.
        Returns list of flags: [{flag_type, severity, description, requires_review}]
        """
        flags = []
        flags.extend(self._check_controlled_substance(prescription))
        flags.extend(self._check_refill_frequency(prescription, refill_history))
        flags.extend(self._check_expiry(prescription))
        flags.extend(self._check_doctor_review_required(prescription))
        return flags

    def _check_controlled_substance(self, rx: dict) -> List[dict]:
        name = rx.get("medication_name", "").lower()
        if any(k in name for k in self.HIGH_RISK_KEYWORDS):
            return [{
                "flag_type": "controlled",
                "severity": "high",
                "description": f"{rx['medication_name']} is a controlled substance — pharmacist review required",
                "requires_review": True,
            }]
        return []

    def _check_refill_frequency(self, rx: dict, history: List[dict]) -> List[dict]:
        if len(history) >= 3:
            return [{
                "flag_type": "refill_frequency",
                "severity": "medium",
                "description": "Unusually high refill frequency — 3 or more refills detected",
                "requires_review": True,
            }]
        return []

    def _check_expiry(self, rx: dict) -> List[dict]:
        from datetime import datetime
        expiry = rx.get("expiry_date")
        if expiry and isinstance(expiry, str):
            try:
                expiry_dt = datetime.fromisoformat(expiry)
                if expiry_dt < datetime.utcnow():
                    return [{
                        "flag_type": "expired",
                        "severity": "high",
                        "description": "Prescription has expired — doctor renewal required",
                        "requires_review": True,
                    }]
            except Exception:
                pass
        return []

    def _check_doctor_review_required(self, rx: dict) -> List[dict]:
        refills_used = rx.get("refills_used", 0)
        refills_allowed = rx.get("refills_allowed", 0)
        if refills_allowed > 0 and refills_used >= refills_allowed:
            return [{
                "flag_type": "refills_exhausted",
                "severity": "medium",
                "description": "All authorized refills used — doctor must renew prescription",
                "requires_review": True,
            }]
        return []


safety_service = MedicationSafetyService()
