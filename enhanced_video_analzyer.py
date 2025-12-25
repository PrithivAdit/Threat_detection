import cv2
import base64
import google.generativeai as genai
import numpy as np
import os
from dotenv import load_dotenv

# Direct environment loading instead of app.settings import
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ... rest of your code remains the same


def extract_sequential_frames(video_path, num_frames=8):
    """Extract 8 high-quality frames strategically distributed across video timeline for sequential analysis"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, f"Could not open video: {video_path}"
    
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    coverage_percentage = (num_frames / total_frames) * 100
    print(f"Video: {total_frames} frames, {duration:.1f}s")
    print(f"Extracting {num_frames} high-quality frames ({coverage_percentage:.1f}% coverage)")
    
    # Strategic frame distribution for sequential analysis
    if total_frames <= num_frames:
        frame_indices = list(range(total_frames))
    else:
        # Distribute frames evenly across video timeline
        frame_indices = np.linspace(0, total_frames-1, num_frames, dtype=int)
    
    for i, target_frame in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            continue
            
        # HIGH QUALITY - NO COMPROMISE (224x224 resolution)
        target_width, target_height = 224, 224  # Increased from 128x128
        resized_frame = cv2.resize(frame, (target_width, target_height), 
                                 interpolation=cv2.INTER_LANCZOS4)  # Better interpolation
        
        # Premium quality compression
        encode_params = [
            cv2.IMWRITE_JPEG_QUALITY, 90,  # Increased from 60 to 90
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ]
        _, buffer = cv2.imencode('.jpg', resized_frame, encode_params)
        frame_b64 = base64.b64encode(buffer).decode('utf-8')
        
        frames.append({
            'mime_type': 'image/jpeg', 
            'data': frame_b64,
            'frame_number': int(target_frame),
            'timestamp': target_frame / fps if fps > 0 else 0
        })
    
    cap.release()
    return frames, None

def get_sequential_description(video_path):
    """Get detailed sequential description using simple API - Step 1 of hybrid approach"""
    # Change the number below (currently 8) to set how many frames to extract, e.g., 15 for 15 frames
    frames, error = extract_sequential_frames(video_path, num_frames = 12)
    
    if error:
        return f"ERROR: {error}"
    
    if not frames:
        return "ERROR: No frames extracted"
    
    # Sequential analysis prompt optimized for surveillance with actual timestamps
    prompt = f"""SURVEILLANCE VIDEO ANALYSIS - SEQUENTIAL EVENT DETECTION

Analyze these {len(frames)} video frames in chronological order. Focus on:

1. SEQUENTIAL EVENTS: Describe what happens in each frame chronologically
2. THREAT PROGRESSION: How does the situation develop over time?
3. KEY ACTORS: People involved and their actions/behaviors
4. OBJECTS & WEAPONS: Any suspicious items, weapons, tools
5. ENVIRONMENTAL CONTEXT: Location, setting, escape routes
6. TEMPORAL ANALYSIS: Is this escalating, stable, or resolving?

Format your response with actual timestamps as:
FRAME 1 ({frames[0]['timestamp']:.1f}s): [detailed description]
FRAME 2 ({frames[1]['timestamp']:.1f}s): [detailed description]
FRAME 3 ({frames[2]['timestamp']:.1f}s): [detailed description]
...

SEQUENTIAL ANALYSIS: [overall progression of events]
THREAT PROGRESSION: [escalating/stable/resolving and why]
KEY FINDINGS: [weapons, violence, suspicious behavior]
ENVIRONMENTAL FACTORS: [location type, number of people, escape routes]
"""
    
    # Create content with frames
    content = [prompt]
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

if __name__ == "__main__":
    # Test the sequential analyzer
    video_path = "videos/armed-robbery.mp4"
    description = get_sequential_description(video_path)
    print("SEQUENTIAL DESCRIPTION:")
    print("="*50)
    print(description)
