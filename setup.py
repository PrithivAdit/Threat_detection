"""
Setup script for video surveillance ADK project
"""

from setuptools import setup, find_packages

setup(
    name="video-surveillance-adk",
    version="1.0.0",
    description="Video surveillance analysis using Google ADK",
    packages=find_packages(),
    install_requires=[
        "google-adk",
        "opencv-python",
        "pillow", 
        "python-dotenv",
        "pandas"
    ],
    python_requires=">=3.8",
)
