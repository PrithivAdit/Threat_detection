#!/usr/bin/env python3
"""
Main entry point for the video surveillance application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.run_batch import process_videos

if __name__ == "__main__":
    print("Starting Video Surveillance Analysis...")
    print("="*50)
    
    # Check if videos directory exists
    if not os.path.exists("videos"):
        print("Creating videos directory...")
        os.makedirs("videos")
        print("Please add your video files to the 'videos' directory and run again.")
        sys.exit(1)
    
    # Run the batch processing
    try:
        results = process_videos()
        print("\n✓ Video analysis completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        sys.exit(1)
