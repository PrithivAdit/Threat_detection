"""
Video Surveillance ADK Application

An agentic approach to video surveillance analysis using Google's Agent Development Kit (ADK).
Processes video files to detect threats and classify incidents.
"""

__version__ = "1.0.0"
__author__ = "Video Surveillance Team"

from .agents.workflow import root_agent
from .run_batch import process_videos

__all__ = ["root_agent", "process_videos"]
