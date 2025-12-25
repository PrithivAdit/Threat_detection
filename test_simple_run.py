#!/usr/bin/env python3
"""
Simple test script to verify the video surveillance setup
"""

import json
import os
import pathlib
import base64
import cv2
import google.generativeai as genai
from src.settings import GOOGLE_API_KEY

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_frames_simple(video_path, max_frames=8):
    """Extract frames directly without complex tool wrapper"""
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Sample frames evenly across the video
    frame_interval = max(1, total_frames // max_frames)
    
    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            frames.append({
                'mime_type': 'image/jpeg',
                'data': frame_b64
            })
        
        frame_count += 1
    
    cap.release()
    return frames

def analyze_video(video_path):
    """Analyze video with proper threat assessment"""
    
    # Extract frames
    frames = extract_frames_simple(video_path)
    
    if not frames:
        return "ERROR: Could not extract frames from video"
    
    # Create content for Gemini
    content = [
        """SURVEILLANCE THREAT ANALYSIS

Analyze these video frames for security threats. Provide:

1. SUMMARY: Chronological description of events
2. THREATS: Specific threats identified (weapons, violence, suspicious behavior)
3. HAZARD: Potential for harm (1-10)
4. EXPOSURE: Number of people/assets at risk (1-10) 
5. VULNERABILITY: How defenseless targets are (1-10)
6. RISK_SCORE: Hazard × Exposure × Vulnerability
7. CLASSIFICATION: Abuse/Assault/Arson/Arrest/Normal

Be specific about what you see in each frame. Look for:
- Weapons (guns, knives, objects used as weapons)
- Violence or aggressive behavior
- Suspicious activities (breaking in, theft, vandalism)
- Number of people involved
- Environmental dangers

Provide concrete analysis based on visual evidence."""
    ]
    
    # Add frames
    for frame in frames:
        content.append({
            'mime_type': frame['mime_type'],
            'data': frame['data']
        })
    
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

def main():
    video_dir = pathlib.Path("videos")
    video_files = list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.avi"))
    
    if not video_files:
        print("No video files found!")
        return
    
    results = {}
    
    for video_file in video_files:
        print(f"\n🎯 ANALYZING: {video_file.name}")
        print("="*50)
        
        analysis = analyze_video(str(video_file))
        results[video_file.name] = analysis
        
        print(analysis)
        print("\n" + "="*50)
    
    # Save results
    os.makedirs("src/results", exist_ok=True)
    with open("src/results/threat_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: src/results/threat_analysis.json")

if __name__ == "__main__":
    main()
