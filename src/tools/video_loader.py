import cv2
import base64
import os
from typing import Dict, Any
from google.adk.tools import FunctionTool

def extract_video_frames(video_path: str, num_frames: int) -> Dict[str, Any]:
    """
    Extract frames from video and return as base64 encoded images with maximum optimization
    
    Args:
        video_path: Path to the video file
        num_frames: Number of frames to extract (max 2)
        
    Returns:
        Dictionary containing base64 encoded frames
    """
    # Enforce maximum limit of 2 frames for aggressive token optimization
    if num_frames is None or num_frames <= 0:
        num_frames = 2  # Default to 2
    elif num_frames > 2:
        num_frames = 2  # Cap at maximum 2 frames
    
    frames_per_prompt = 25  # Increased sampling for better frame distribution
    
    if not os.path.exists(video_path):
        return {"error": f"Video file not found: {video_path}"}
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": f"Could not open video: {video_path}"}
    
    frames = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    try:
        while cap.isOpened() and len(frames) < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frames_per_prompt == 0:
                # AGGRESSIVE OPTIMIZATION FOR MAXIMUM TOKEN REDUCTION
                # Ultra-small resolution to minimize base64 size
                target_width = 96   # Reduced from 256 to 96 (85% smaller)
                target_height = 96  # Reduced from 256 to 96 (85% smaller)
                resized_frame = cv2.resize(frame, (target_width, target_height))
                
                # Maximum compression with lowest quality
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, 20]  # Reduced from 50 to 20
                _, buffer = cv2.imencode('.jpg', resized_frame, encode_params)
                
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                frames.append(frame_b64)
            
            frame_count += 1
            
    except Exception as e:
        cap.release()
        return {"error": f"Error processing video frames: {str(e)}"}
        
    finally:
        cap.release()
    
    if not frames:
        return {"error": "No frames could be extracted from the video"}
    
    return {
        "frames": frames,
        "total_frames": frame_count,
        "sampled_frames": len(frames),
        "video_duration_frames": total_frames,
        "optimization_info": {
            "frame_size": f"{target_width}x{target_height}",
            "jpeg_quality": 20,
            "optimization_level": "maximum",
            "token_reduction": "~85%"
        }
    }

# Create the tool using FunctionTool (removed incompatible parameters)
VideoFrameTool = FunctionTool(extract_video_frames)
