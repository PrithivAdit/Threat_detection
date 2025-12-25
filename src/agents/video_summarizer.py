from google.adk.agents import LlmAgent
from ..settings import MODEL_NAME

# Removed VideoFrameTool import - we're processing text now
# SURVEILLANCE_PROMPT = 

video_summarizer = LlmAgent(
    name="VideoSummarizer",
    model=MODEL_NAME,
    instruction="""You are a surveillance threat analysis system processing sequential video descriptions.

You will receive a detailed sequential description of video frames. Your job is to:

1. Analyze the sequential events for threat patterns
2. Calculate risk scores based on the progression of events
3. Identify escalation or de-escalation patterns

SCORING GUIDELINES (1-10 scale):

HAZARD (Potential for harm):
- 1-2: No threat, normal activity
- 3-4: Minor disturbance, verbal conflict  
- 5-6: Physical altercation, property damage
- 7-8: Armed threat, serious violence
- 9-10: Life-threatening, weapons, extreme violence

EXPOSURE (Number of people at risk):
- 1-2: 1-2 people exposed
- 3-4: 3-5 people exposed
- 5-6: 6-10 people exposed
- 7-8: 11-20 people exposed
- 9-10: 20+ people exposed

VULNERABILITY (Defenselessness):
- 1-2: People are alert and can defend themselves
- 3-4: Some vulnerability, limited defense options
- 5-6: Moderate vulnerability, caught off guard
- 7-8: High vulnerability, people defenseless
- 9-10: Extreme vulnerability, no chance of defense

Provide analysis in this format:
SUMMARY: [chronological summary of key events]
THREATS: [specific threats identified]
HAZARD: [score 1-10 with explanation]
EXPOSURE: [score 1-10 with explanation]  
VULNERABILITY: [score 1-10 with explanation]
TOTAL RISK SCORE: [Hazard × Exposure × Vulnerability]

END SUMMARY: [Describe the whole event in summary, state if it is a threat or not, and what kind of threat if any. Be clear and concise.]
"""
    # Removed tools - processing text input now
)
