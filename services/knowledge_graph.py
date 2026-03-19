"""
Simple Knowledge Graph - Disease-Symptom-Drug Relationships

A lightweight knowledge graph for medical relationships without
requiring Neo4j or other graph databases.
"""
from typing import Dict, List
from loguru import logger


class MedicalKnowledgeGraph:
    """
    Simple in-memory knowledge graph for medical relationships.

    Tracks:
    - Diseases and their symptoms
    - Drugs and what they treat
    - Drug side effects
    - Contraindications
    """

    def __init__(self):
        """Initialize knowledge graph with common medical relationships"""

        # Disease -> Symptoms
        self.disease_symptoms = {
            "diabetes": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing"],
            "hypertension": ["headache", "dizziness", "chest pain", "shortness of breath", "nosebleeds"],
            "asthma": ["wheezing", "shortness of breath", "chest tightness", "coughing"],
            "migraine": ["severe headache", "nausea", "sensitivity to light", "visual disturbances"],
            "flu": ["fever", "cough", "sore throat", "body aches", "fatigue"],
            "covid-19": ["fever", "cough", "loss of taste", "loss of smell", "fatigue", "shortness of breath"],
            "heart disease": ["chest pain", "shortness of breath", "fatigue", "irregular heartbeat"],
            "depression": ["sadness", "loss of interest", "fatigue", "sleep problems", "appetite changes"],
            "anxiety": ["worry", "restlessness", "rapid heartbeat", "sweating", "difficulty concentrating"]
        }

        # Drug -> Treats (diseases)
        self.drug_treats = {
            "metformin": ["diabetes", "prediabetes"],
            "lisinopril": ["hypertension", "heart disease"],
            "albuterol": ["asthma", "copd"],
            "sumatriptan": ["migraine"],
            "ibuprofen": ["pain", "inflammation", "fever"],
            "aspirin": ["pain", "fever", "heart disease prevention"],
            "sertraline": ["depression", "anxiety"],
            "atorvastatin": ["high cholesterol", "heart disease prevention"]
        }

        # Drug -> Side Effects
        self.drug_side_effects = {
            "metformin": ["nausea", "diarrhea", "stomach upset"],
            "lisinopril": ["dizziness", "dry cough", "fatigue"],
            "albuterol": ["tremor", "nervousness", "rapid heartbeat"],
            "sumatriptan": ["dizziness", "drowsiness", "tingling"],
            "ibuprofen": ["stomach upset", "heartburn", "dizziness"],
            "aspirin": ["stomach upset", "bleeding risk"],
            "sertraline": ["nausea", "insomnia", "drowsiness"],
            "atorvastatin": ["muscle pain", "liver problems"]
        }

        # Symptom -> Possible Diseases
        self.symptom_diseases = {}
        for disease, symptoms in self.disease_symptoms.items():
            for symptom in symptoms:
                if symptom not in self.symptom_diseases:
                    self.symptom_diseases[symptom] = []
                self.symptom_diseases[symptom].append(disease)

        logger.info(f"[KnowledgeGraph] Initialized with {len(self.disease_symptoms)} diseases, "
                   f"{len(self.drug_treats)} drugs")

    def get_disease_symptoms(self, disease: str) -> List[str]:
        """Get symptoms for a disease"""
        disease_lower = disease.lower()
        return self.disease_symptoms.get(disease_lower, [])

    def get_possible_diseases(self, symptoms: List[str]) -> Dict[str, int]:
        """
        Get possible diseases based on symptoms.

        Returns dict of disease -> symptom match count
        """
        disease_matches = {}

        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for possible_disease in self.symptom_diseases.get(symptom_lower, []):
                disease_matches[possible_disease] = disease_matches.get(possible_disease, 0) + 1

        # Sort by match count
        return dict(sorted(disease_matches.items(), key=lambda x: x[1], reverse=True))

    def get_drug_info(self, drug: str) -> Dict:
        """Get comprehensive drug information"""
        drug_lower = drug.lower()

        return {
            "drug": drug,
            "treats": self.drug_treats.get(drug_lower, []),
            "side_effects": self.drug_side_effects.get(drug_lower, []),
            "found": drug_lower in self.drug_treats
        }

    def get_treatment_options(self, disease: str) -> List[str]:
        """Get drugs that treat a disease"""
        disease_lower = disease.lower()
        treatments = []

        for drug, treats in self.drug_treats.items():
            if disease_lower in treats:
                treatments.append(drug)

        return treatments

    def enhance_query_with_graph(self, query: str) -> str:
        """
        Enhance a query with knowledge graph context.

        Adds relevant medical relationships to improve RAG retrieval.
        """
        query_lower = query.lower()
        context_parts = []

        # Check for diseases mentioned
        for disease in self.disease_symptoms.keys():
            if disease in query_lower:
                symptoms = self.disease_symptoms[disease]
                context_parts.append(f"{disease} symptoms: {', '.join(symptoms[:5])}")

                # Add treatments
                treatments = self.get_treatment_options(disease)
                if treatments:
                    context_parts.append(f"{disease} treatments: {', '.join(treatments[:3])}")

        # Check for drugs mentioned
        for drug in self.drug_treats.keys():
            if drug in query_lower:
                info = self.get_drug_info(drug)
                if info["treats"]:
                    context_parts.append(f"{drug} treats: {', '.join(info['treats'])}")

        # Check for symptoms mentioned
        mentioned_symptoms = []
        for symptom in self.symptom_diseases.keys():
            if symptom in query_lower:
                mentioned_symptoms.append(symptom)

        if mentioned_symptoms:
            possible_diseases = self.get_possible_diseases(mentioned_symptoms)
            if possible_diseases:
                top_diseases = list(possible_diseases.keys())[:3]
                context_parts.append(f"Symptoms may indicate: {', '.join(top_diseases)}")

        # Combine context
        if context_parts:
            enhanced = f"{query}\n\nMedical context: {' | '.join(context_parts)}"
            logger.info(f"[KnowledgeGraph] Enhanced query with {len(context_parts)} context items")
            return enhanced

        return query

    def add_disease(self, disease: str, symptoms: List[str]):
        """Add or update a disease and its symptoms"""
        disease_lower = disease.lower()
        self.disease_symptoms[disease_lower] = symptoms

        # Update reverse index
        for symptom in symptoms:
            if symptom not in self.symptom_diseases:
                self.symptom_diseases[symptom] = []
            if disease_lower not in self.symptom_diseases[symptom]:
                self.symptom_diseases[symptom].append(disease_lower)

        logger.info(f"[KnowledgeGraph] Added/updated disease: {disease}")

    def add_drug(self, drug: str, treats: List[str], side_effects: List[str]):
        """Add or update a drug"""
        drug_lower = drug.lower()
        self.drug_treats[drug_lower] = treats
        self.drug_side_effects[drug_lower] = side_effects

        logger.info(f"[KnowledgeGraph] Added/updated drug: {drug}")


# Singleton instance
knowledge_graph = MedicalKnowledgeGraph()
