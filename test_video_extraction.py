from src.tools.video_loader import extract_video_frames
import json

def test_video_extraction(video_path):
    print(f"Testing video extraction for: {video_path}")
    result = extract_video_frames(video_path)
    
    # Print basic info
    print("\nExtraction Results:")
    print(f"Total frames in video: {result.get('total_frames', 0)}")
    print(f"Number of frames extracted: {result.get('sampled_frames', 0)}")
    
    # Print first frame as base64 (truncated for readability)
    if 'frames' in result and result['frames']:
        first_frame = result['frames'][0]
        print("\nFirst frame base64 (first 50 chars):", first_frame[:50] + "...")
    else:
        print("\nNo frames were extracted!")
        
    if 'error' in result:
        print("\nError occurred:", result['error'])

if __name__ == "__main__":
    # Using the actual video file in the workspace
    video_path = "videos/armed-robbery.mp4"
    test_video_extraction(video_path) 