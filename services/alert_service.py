"""
Clinical Alert Engine - Detects dangerous medical situations.

Features:
- Emergency symptom detection
- Drug interaction warnings
- Abnormal value alerts
- Multi-condition risk assessment
"""
from typing import Dict, List, Optional
from enum import Enum
from loguru import logger


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # Immediate medical attention required
    HIGH = "high"          # Urgent medical consultation needed
    MEDIUM = "medium"      # Schedule appointment soon
    LOW = "low"            # Monitor and follow up


class AlertType(str, Enum):
    """Types of clinical alerts"""
    EMERGENCY_SYMPTOM = "emergency_symptom"
    DRUG_INTERACTION = "drug_interaction"
    ABNORMAL_LAB_VALUE = "abnormal_lab_value"
    MULTI_SYMPTOM_RISK = "multi_symptom_risk"
    CONTRAINDICATION = "contraindication"


class ClinicalAlertEngine:
    """
    Detects dangerous medical situations and generates alerts.

    Monitors:
    - Emergency symptoms
    - Drug interactions
    - Abnormal lab values
    - Multi-condition risks
    """

    # Emergency symptoms requiring immediate attention
    EMERGENCY_SYMPTOMS = {
        "chest pain": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "difficulty breathing": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "severe bleeding": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "loss of consciousness": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "stroke symptoms": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "severe head injury": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "seizure": {"severity": AlertSeverity.CRITICAL, "action": "Call 911 immediately"},
        "suicidal thoughts": {"severity": AlertSeverity.CRITICAL, "action": "Call 988 or 911 immediately"},
        "severe allergic reaction": {"severity": AlertSeverity.CRITICAL, "action": "Use EpiPen and call 911"},
        "sudden severe headache": {"severity": AlertSeverity.HIGH, "action": "Seek emergency care"},
        "confusion or disorientation": {"severity": AlertSeverity.HIGH, "action": "Seek emergency care"},
        "severe abdominal pain": {"severity": AlertSeverity.HIGH, "action": "Seek emergency care"},
        "high fever": {"severity": AlertSeverity.HIGH, "action": "Seek urgent medical care"},
        "persistent vomiting": {"severity": AlertSeverity.MEDIUM, "action": "Contact doctor today"}
    }

    # Known dangerous drug interactions
    DRUG_INTERACTIONS = {
        ("warfarin", "aspirin"): {
            "severity": AlertSeverity.HIGH,
            "warning": "Increased bleeding risk",
            "action": "Consult doctor before combining"
        },
        ("metformin", "alcohol"): {
            "severity": AlertSeverity.MEDIUM,
            "warning": "Risk of lactic acidosis",
            "action": "Avoid alcohol or consult doctor"
        },
        ("ssri", "maoi"): {
            "severity": AlertSeverity.CRITICAL,
            "warning": "Serotonin syndrome risk",
            "action": "Do not combine - seek immediate medical advice"
        },
        ("statin", "grapefruit"): {
            "severity": AlertSeverity.MEDIUM,
            "warning": "Increased statin levels",
            "action": "Avoid grapefruit or consult doctor"
        }
    }

    # Critical lab value thresholds
    CRITICAL_LAB_VALUES = {
        "glucose": {"critical_high": 400, "critical_low": 40, "unit": "mg/dL"},
        "potassium": {"critical_high": 6.0, "critical_low": 2.5, "unit": "mmol/L"},
        "sodium": {"critical_high": 160, "critical_low": 120, "unit": "mmol/L"},
        "creatinine": {"critical_high": 5.0, "critical_low": None, "unit": "mg/dL"},
        "hemoglobin": {"critical_high": 20, "critical_low": 7, "unit": "g/dL"},
        "platelets": {"critical_high": 1000, "critical_low": 50, "unit": "K/μL"},
        "wbc": {"critical_high": 30, "critical_low": 2, "unit": "K/μL"}
    }

    def __init__(self):
        logger.info("[AlertEngine] Clinical Alert Engine initialized")

    def check_query(self, query: str) -> List[Dict]:
        """
        Check query for emergency symptoms.

        Args:
            query: User's query text

        Returns:
            List of alerts
        """
        alerts = []
        query_lower = query.lower()

        for symptom, info in self.EMERGENCY_SYMPTOMS.items():
            if symptom in query_lower:
                alerts.append({
                    "type": AlertType.EMERGENCY_SYMPTOM,
                    "severity": info["severity"],
                    "symptom": symptom,
                    "message": f"Emergency symptom detected: {symptom}",
                    "action": info["action"],
                    "timestamp": self._get_timestamp()
                })
                logger.warning(f"[AlertEngine] Emergency symptom detected: {symptom}")

        return alerts

    def check_drug_interaction(self, medications: List[str]) -> List[Dict]:
        """
        Check for dangerous drug interactions.

        Args:
            medications: List of medication names

        Returns:
            List of interaction alerts
        """
        alerts = []
        meds_lower = [med.lower() for med in medications]

        # Check all pairs
        for i, med1 in enumerate(meds_lower):
            for med2 in meds_lower[i+1:]:
                # Check direct match
                interaction = self.DRUG_INTERACTIONS.get((med1, med2)) or \
                             self.DRUG_INTERACTIONS.get((med2, med1))

                if interaction:
                    alerts.append({
                        "type": AlertType.DRUG_INTERACTION,
                        "severity": interaction["severity"],
                        "drugs": [medications[meds_lower.index(med1)],
                                 medications[meds_lower.index(med2)]],
                        "warning": interaction["warning"],
                        "action": interaction["action"],
                        "timestamp": self._get_timestamp()
                    })
                    logger.warning(f"[AlertEngine] Drug interaction: {med1} + {med2}")

                # Check for drug class interactions
                else:
                    class_interaction = self._check_drug_class_interaction(med1, med2)
                    if class_interaction:
                        alerts.append(class_interaction)

        return alerts

    def check_lab_values(self, lab_values: List[Dict]) -> List[Dict]:
        """
        Check lab values for critical abnormalities.

        Args:
            lab_values: List of lab results with name, value, unit

        Returns:
            List of critical value alerts
        """
        alerts = []

        for lab in lab_values:
            name = lab.get("name", "").lower()
            value = lab.get("value")

            # Try to extract numeric value
            try:
                if isinstance(value, str):
                    # Extract number from string like "150 mg/dL"
                    numeric_value = float(''.join(c for c in value.split()[0] if c.isdigit() or c == '.'))
                else:
                    numeric_value = float(value)
            except (ValueError, IndexError, TypeError):
                continue

            # Check against critical thresholds
            for test_name, thresholds in self.CRITICAL_LAB_VALUES.items():
                if test_name in name:
                    critical_high = thresholds.get("critical_high")
                    critical_low = thresholds.get("critical_low")

                    if critical_high and numeric_value >= critical_high:
                        alerts.append({
                            "type": AlertType.ABNORMAL_LAB_VALUE,
                            "severity": AlertSeverity.CRITICAL,
                            "test": lab.get("name"),
                            "value": value,
                            "threshold": f"Critical high: ≥{critical_high} {thresholds['unit']}",
                            "message": f"Critically high {test_name}: {value}",
                            "action": "Seek immediate medical attention",
                            "timestamp": self._get_timestamp()
                        })
                        logger.error(f"[AlertEngine] Critical high {test_name}: {value}")

                    elif critical_low and numeric_value <= critical_low:
                        alerts.append({
                            "type": AlertType.ABNORMAL_LAB_VALUE,
                            "severity": AlertSeverity.CRITICAL,
                            "test": lab.get("name"),
                            "value": value,
                            "threshold": f"Critical low: ≤{critical_low} {thresholds['unit']}",
                            "message": f"Critically low {test_name}: {value}",
                            "action": "Seek immediate medical attention",
                            "timestamp": self._get_timestamp()
                        })
                        logger.error(f"[AlertEngine] Critical low {test_name}: {value}")

        return alerts

    def check_multi_symptom_risk(self, symptoms: List[str]) -> List[Dict]:
        """
        Check for dangerous symptom combinations.

        Args:
            symptoms: List of symptoms

        Returns:
            List of multi-symptom risk alerts
        """
        alerts = []
        symptoms_lower = [s.lower() for s in symptoms]

        # Stroke warning signs (FAST)
        stroke_symptoms = ["facial drooping", "arm weakness", "speech difficulty", "sudden confusion"]
        if any(s in ' '.join(symptoms_lower) for s in stroke_symptoms):
            alerts.append({
                "type": AlertType.MULTI_SYMPTOM_RISK,
                "severity": AlertSeverity.CRITICAL,
                "condition": "Possible stroke",
                "message": "Stroke warning signs detected",
                "action": "Call 911 immediately - Time is critical",
                "timestamp": self._get_timestamp()
            })

        # Heart attack symptoms
        heart_attack_symptoms = ["chest pain", "shortness of breath", "nausea", "cold sweat"]
        matching_heart = sum(1 for s in heart_attack_symptoms if s in ' '.join(symptoms_lower))
        if matching_heart >= 2:
            alerts.append({
                "type": AlertType.MULTI_SYMPTOM_RISK,
                "severity": AlertSeverity.CRITICAL,
                "condition": "Possible heart attack",
                "message": "Multiple heart attack symptoms detected",
                "action": "Call 911 immediately",
                "timestamp": self._get_timestamp()
            })

        # Sepsis warning
        sepsis_symptoms = ["high fever", "rapid heart rate", "confusion", "extreme pain"]
        matching_sepsis = sum(1 for s in sepsis_symptoms if s in ' '.join(symptoms_lower))
        if matching_sepsis >= 2:
            alerts.append({
                "type": AlertType.MULTI_SYMPTOM_RISK,
                "severity": AlertSeverity.HIGH,
                "condition": "Possible sepsis",
                "message": "Multiple sepsis warning signs detected",
                "action": "Seek emergency medical care immediately",
                "timestamp": self._get_timestamp()
            })

        return alerts

    def _check_drug_class_interaction(self, drug1: str, drug2: str) -> Optional[Dict]:
        """Check for drug class interactions"""
        # Common SSRI names
        ssris = ["fluoxetine", "sertraline", "paroxetine", "citalopram", "escitalopram"]
        # Common MAOI names
        maois = ["phenelzine", "tranylcypromine", "isocarboxazid", "selegiline"]

        if (drug1 in ssris and drug2 in maois) or (drug1 in maois and drug2 in ssris):
            return {
                "type": AlertType.DRUG_INTERACTION,
                "severity": AlertSeverity.CRITICAL,
                "drugs": [drug1, drug2],
                "warning": "SSRI + MAOI: Serotonin syndrome risk",
                "action": "Do not combine - seek immediate medical advice",
                "timestamp": self._get_timestamp()
            }

        return None

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def generate_alert_summary(self, alerts: List[Dict]) -> Dict:
        """
        Generate summary of all alerts.

        Args:
            alerts: List of alerts

        Returns:
            Alert summary with highest severity and counts
        """
        if not alerts:
            return {
                "has_alerts": False,
                "highest_severity": None,
                "total_alerts": 0,
                "by_severity": {},
                "by_type": {}
            }

        # Count by severity
        by_severity = {}
        for alert in alerts:
            severity = alert.get("severity")
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Count by type
        by_type = {}
        for alert in alerts:
            alert_type = alert.get("type")
            by_type[alert_type] = by_type.get(alert_type, 0) + 1

        # Determine highest severity
        severity_order = [AlertSeverity.CRITICAL, AlertSeverity.HIGH, AlertSeverity.MEDIUM, AlertSeverity.LOW]
        highest_severity = None
        for sev in severity_order:
            if sev in by_severity:
                highest_severity = sev
                break

        return {
            "has_alerts": True,
            "highest_severity": highest_severity,
            "total_alerts": len(alerts),
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_count": by_severity.get(AlertSeverity.CRITICAL, 0),
            "requires_immediate_action": highest_severity == AlertSeverity.CRITICAL
        }


# Singleton instance
alert_engine = ClinicalAlertEngine()
