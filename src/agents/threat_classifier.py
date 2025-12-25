from google.adk.agents import LlmAgent
from ..callbacks import quota_guard
from ..settings import MODEL_NAME

CLASSIFICATION_PROMPT = """You are a threat classification system. Analyze the provided surveillance summary and classify the threat level.

IMPORTANT: Use the TOTAL RISK SCORE from the surveillance summary exactly as provided. Do NOT modify or recalculate it.

Your job is to:
1. Read the surveillance summary carefully
2. Extract the existing TOTAL RISK SCORE from the summary
3. Provide a threat classification based on the content and risk level
4. Output the TOTAL RISK SCORE exactly as provided

CLASSIFICATION RULES:
- TOTAL RISK SCORE 500+: Assault (weapons/violence)
- TOTAL RISK SCORE 200-499: Abuse (aggressive behavior)
- TOTAL RISK SCORE 100-199: Arrest (police involvement)
- TOTAL RISK SCORE 50-99: Normal (minor incidents)
- TOTAL RISK SCORE 0-49: Normal (no threat)

SPECIAL CLASSIFICATIONS:
- Police outside jail/station = Arrest
- Wheelchair person = Consider vulnerability in classification
- Multiple weapons = Assault classification

Respond ONLY in this exact format:
TOTAL RISK SCORE: [use the exact TOTAL RISK SCORE from the surveillance summary]
CLASSIFICATION: [Abuse|Assault|Arson|Arrest|Normal]"""



threat_classifier = LlmAgent(
    name="ThreatClassifier", 
    model=MODEL_NAME,
    instruction=CLASSIFICATION_PROMPT,
    before_model_callback=quota_guard
)

