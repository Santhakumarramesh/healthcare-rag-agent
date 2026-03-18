"""
Sample Healthcare FAQ data for bootstrapping the vector store.
Replace or extend with your own PDFs/documents via the ingestion pipeline.
"""

MEDICAL_FAQ_DOCUMENTS = [
    {
        "id": "faq_001",
        "category": "General Health",
        "question": "What are common symptoms of Type 2 Diabetes?",
        "answer": (
            "Common symptoms of Type 2 Diabetes include: increased thirst and frequent urination, "
            "unexplained weight loss, fatigue and lack of energy, blurred vision, slow-healing sores "
            "or frequent infections, tingling or numbness in hands or feet (peripheral neuropathy), "
            "and areas of darkened skin (acanthosis nigricans). Many people with Type 2 Diabetes have "
            "no symptoms initially, which is why regular screening is important. If you experience "
            "these symptoms, consult your healthcare provider for a proper diagnosis."
        ),
    },
    {
        "id": "faq_002",
        "category": "Medications",
        "question": "What is Metformin and what is it used for?",
        "answer": (
            "Metformin is a first-line oral medication used to treat Type 2 Diabetes. It works by "
            "reducing glucose production in the liver, improving insulin sensitivity, and decreasing "
            "intestinal glucose absorption. Metformin is also used off-label for polycystic ovary "
            "syndrome (PCOS) and prediabetes. Common side effects include nausea, diarrhea, and "
            "stomach upset, which usually improve over time. It should be taken with food to reduce "
            "GI side effects. Always follow your doctor's prescribed dosage."
        ),
    },
    {
        "id": "faq_003",
        "category": "Preventive Care",
        "question": "How often should adults get a physical examination?",
        "answer": (
            "The recommended frequency for adult physical exams varies by age and health status. "
            "Generally: Ages 18-39 (healthy adults): every 2-3 years. Ages 40-49: every 1-2 years. "
            "Ages 50+: annually. However, if you have chronic conditions (diabetes, hypertension, heart "
            "disease), your doctor may recommend more frequent visits. Annual wellness visits are covered "
            "by most insurance plans under the Affordable Care Act. Regular checkups help detect "
            "conditions early when they're most treatable."
        ),
    },
    {
        "id": "faq_004",
        "category": "Mental Health",
        "question": "What are the signs of clinical depression?",
        "answer": (
            "Clinical depression (Major Depressive Disorder) signs include: persistent sadness or empty "
            "mood lasting 2+ weeks, loss of interest in previously enjoyed activities (anhedonia), "
            "significant weight changes, sleep disturbances (insomnia or oversleeping), fatigue or "
            "loss of energy, feelings of worthlessness or excessive guilt, difficulty concentrating, "
            "and in severe cases, thoughts of death or suicide. Depression is a medical condition, not "
            "a character flaw. If you or someone you know shows these signs, please seek professional "
            "help. Crisis line: 988 Suicide & Crisis Lifeline."
        ),
    },
    {
        "id": "faq_005",
        "category": "Cardiology",
        "question": "What are warning signs of a heart attack?",
        "answer": (
            "Heart attack warning signs include: chest pain, pressure, tightness, or discomfort "
            "(can be mild or severe), pain radiating to arm (usually left), jaw, neck, or back, "
            "shortness of breath with or without chest discomfort, cold sweat, nausea, or lightheadedness. "
            "Women may experience atypical symptoms: unusual fatigue, nausea, vomiting, or back/jaw pain "
            "without obvious chest pain. CRITICAL: Call 911 immediately if you suspect a heart attack. "
            "Do not drive yourself. Chew aspirin (325mg) if not allergic and advised by emergency services. "
            "Time is muscle — every minute matters."
        ),
    },
    {
        "id": "faq_006",
        "category": "Nutrition",
        "question": "What is the recommended daily water intake?",
        "answer": (
            "The general recommendation is about 3.7 liters (125 oz) per day for men and 2.7 liters "
            "(91 oz) per day for women, including water from all beverages and food sources. The common "
            "'8 glasses a day' rule is a simplified guideline. Your actual needs depend on: activity "
            "level, climate and heat exposure, overall health, pregnancy or breastfeeding status. "
            "Signs of adequate hydration include pale yellow urine and rarely feeling thirsty. "
            "Increase intake during exercise, hot weather, illness with fever, or when pregnant."
        ),
    },
    {
        "id": "faq_007",
        "category": "Medications",
        "question": "Can I take ibuprofen and acetaminophen together?",
        "answer": (
            "Yes, ibuprofen (Advil, Motrin) and acetaminophen (Tylenol) can generally be taken together "
            "because they work via different mechanisms. Ibuprofen is an NSAID that reduces inflammation, "
            "while acetaminophen works centrally for pain relief. This combination is sometimes used for "
            "moderate to severe pain (e.g., post-surgical or dental). However: follow recommended doses "
            "for each medication separately, avoid ibuprofen if you have kidney issues, ulcers, or take "
            "blood thinners, avoid exceeding 4,000mg of acetaminophen daily (3,000mg if elderly or "
            "drinking alcohol). Always consult your pharmacist or doctor before combining medications."
        ),
    },
    {
        "id": "faq_008",
        "category": "Preventive Care",
        "question": "What vaccines are recommended for adults?",
        "answer": (
            "Key adult vaccines recommended by the CDC include: Annual flu shot (everyone 6+ months), "
            "COVID-19 (updated boosters as recommended), Tdap (tetanus, diphtheria, pertussis) every 10 years, "
            "Shingles vaccine (Shingrix) — 2 doses for adults 50+, Pneumococcal vaccine for adults 65+, "
            "RSV vaccine for adults 60+, HPV vaccine through age 26 (or up to 45 with doctor consultation), "
            "Hepatitis A and B if not previously vaccinated. Travel vaccines vary by destination. "
            "Check your vaccination history with your doctor and use the CDC Adult Immunization Schedule "
            "at cdc.gov for personalized recommendations."
        ),
    },
    {
        "id": "faq_009",
        "category": "General Health",
        "question": "What is hypertension and what are safe blood pressure ranges?",
        "answer": (
            "Hypertension (high blood pressure) is when blood pressure consistently reads 130/80 mmHg "
            "or higher. Blood pressure categories: Normal: Less than 120/80 mmHg. Elevated: 120-129 / "
            "less than 80. Stage 1 Hypertension: 130-139 / 80-89. Stage 2 Hypertension: 140+ / 90+. "
            "Hypertensive Crisis: 180+ / 120+ (seek emergency care). Hypertension is called the 'silent "
            "killer' because it often has no symptoms. Long-term, it damages arteries and increases risk "
            "of heart attack, stroke, and kidney disease. Management includes lifestyle changes (diet, "
            "exercise, sodium reduction) and medications (ACE inhibitors, beta blockers, diuretics)."
        ),
    },
    {
        "id": "faq_010",
        "category": "Women's Health",
        "question": "What are symptoms of polycystic ovary syndrome (PCOS)?",
        "answer": (
            "PCOS is a hormonal disorder affecting 1 in 10 women of reproductive age. Common symptoms "
            "include: irregular or missed periods, excess androgen (elevated male hormones) causing "
            "excess facial/body hair (hirsutism), severe acne, or male-pattern baldness, polycystic "
            "ovaries visible on ultrasound (enlarged ovaries with many follicles), weight gain especially "
            "around the midsection, skin darkening in body creases, and skin tags. PCOS is a leading "
            "cause of infertility. It's also linked to insulin resistance, Type 2 Diabetes, and "
            "cardiovascular disease. Diagnosis requires 2 of 3 criteria: irregular periods, high "
            "androgens, or polycystic ovaries. Treatment is individualized."
        ),
    },
    {
        "id": "faq_011",
        "category": "Emergency",
        "question": "What are signs of a stroke and what should I do?",
        "answer": (
            "Use the FAST acronym to identify stroke symptoms: F - Face drooping (one side droops or "
            "is numb, uneven smile), A - Arm weakness (one arm drifts down when both are raised), "
            "S - Speech difficulty (slurred, strange, or inability to speak), T - Time to call 911. "
            "Additional symptoms: sudden severe headache with no known cause, sudden vision problems, "
            "sudden dizziness or loss of balance. CRITICAL: Call 911 immediately. Note the time symptoms "
            "started — this determines treatment options. Clot-busting medication (tPA) must be given "
            "within 3-4.5 hours of symptom onset. Do not give food or water. Do not let the person "
            "drive. Every second counts — brain cells die rapidly during stroke."
        ),
    },
    {
        "id": "faq_012",
        "category": "Mental Health",
        "question": "What is the difference between anxiety and an anxiety disorder?",
        "answer": (
            "Normal anxiety is a natural stress response — feeling nervous before a presentation or "
            "worried about a medical test. It's temporary and proportional to the situation. Anxiety "
            "disorders involve excessive, persistent fear or worry that interferes with daily life. "
            "Types include: Generalized Anxiety Disorder (GAD) — excessive worry about many things, "
            "Panic Disorder — recurrent unexpected panic attacks, Social Anxiety Disorder — intense "
            "fear of social situations, Specific Phobias, and PTSD. Signs that anxiety has become "
            "a disorder: it's difficult to control, it lasts 6+ months, it causes physical symptoms "
            "(racing heart, sweating), and it impairs work, school, or relationships. "
            "Effective treatments include CBT, therapy, and medication."
        ),
    },
]


def get_documents_as_text() -> list[dict]:
    """Format FAQ documents for ingestion into the vector store."""
    docs = []
    for item in MEDICAL_FAQ_DOCUMENTS:
        text = (
            f"Category: {item['category']}\n"
            f"Question: {item['question']}\n"
            f"Answer: {item['answer']}"
        )
        docs.append({
            "text": text,
            "metadata": {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "source": "Healthcare FAQ Database v1.0",
            }
        })
    return docs
