from google.adk.agents import SequentialAgent
from .video_summarizer import video_summarizer
from .threat_classifier import threat_classifier

# Create the sequential workflow agent
root_agent = SequentialAgent(
    name="VideoSurveillanceWorkflow",
    description="Analyzes video for surveillance threats and classifies incidents",
    sub_agents=[video_summarizer, threat_classifier]
)
