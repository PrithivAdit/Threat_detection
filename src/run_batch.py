#run_batch.py
import json
import os
import pathlib
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .agents.workflow import root_agent
from .agents.video_summarizer import video_summarizer
from .agents.threat_classifier import threat_classifier
from .tools.video_loader import extract_video_frames
from .settings import GOOGLE_API_KEY
from google.genai import types
import asyncio
import time

async def process_videos_async(video_directory: str = "videos", output_file: str = "src/results/video_analysis_results.json"):
    """
    Process all videos in the specified directory with enhanced error handling and proper workflow
    """
    
    # Initialize session service
    session_service = InMemorySessionService()
    
    # Create separate runners for each agent to handle failures independently
    video_runner = Runner(
        agent=video_summarizer,
        app_name="video_analysis", 
        session_service=session_service
    )
    
    threat_runner = Runner(
        agent=threat_classifier,
        app_name="threat_classification",
        session_service=session_service
    )
    
    # Find all video files
    video_path = pathlib.Path(video_directory)
    video_files = list(video_path.glob("*.mp4")) + list(video_path.glob("*.avi")) + list(video_path.glob("*.mov"))
    
    if not video_files:
        print(f"No video files found in {video_directory}")
        return {}
    
    results = {}
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\nProcessing {i}/{len(video_files)}: {video_file.name}")
        
        try:
            # Create session for video analysis
            video_session = await session_service.create_session(
                app_name="video_analysis",
                user_id="surveillance_user",
                session_id=f"video_{video_file.stem}"
            )
            
            print(f"✓ Created video analysis session: {video_session.id}")
            
            # Extract frames first using the video_loader
            print(f"📹 Extracting frames from: {str(video_file)}")
            
            frame_result = extract_video_frames(str(video_file), num_frames=3)
            
            if 'error' in frame_result:
                print(f"❌ Frame extraction failed: {frame_result['error']}")
                video_analysis_result = f"""FRAME EXTRACTION ERROR for {video_file.name}:
ERROR: {frame_result['error']}
SUMMARY: Unable to process video file - file may be corrupted or in unsupported format
THREATS: Manual review required due to technical failure
HAZARD: 5 (Unknown - requires manual inspection)
EXPOSURE: 5 (Unknown - requires manual inspection) 
VULNERABILITY: 5 (Unknown - requires manual inspection)
RISK_SCORE: 125 (Fallback score due to extraction failure)"""
                
                print("🔄 Skipping video analysis due to frame extraction failure")
                
            else:
                print(f"✅ Extracted {frame_result['sampled_frames']} frames successfully")
                
                # Create message in plain text format
                user_message = types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=f"Analyze this video for surveillance threats.\n\nVIDEO_PATH={str(video_file)}\n\nPlease use the exact VIDEO_PATH value above to call extract_video_frames.")
                    ]
                )
                
                print(f"📤 Sending video analysis request...")
                
                # Run video analysis with retry logic
                video_analysis_result = ""
                max_retries = 3
                
                for attempt in range(max_retries):
                    try:
                        print(f"🔄 Video analysis attempt {attempt + 1}/{max_retries}")
                        
                        events = video_runner.run(
                            user_id="surveillance_user",
                            session_id=video_session.id,
                            new_message=user_message
                        )
                        
                        # Process video analysis events
                        for event in events:
                            if hasattr(event, 'error_code') and event.error_code:
                                print(f"⚠️ Video analysis error: {event.error_code}")
                                if event.error_code == 'MALFORMED_FUNCTION_CALL':
                                    print("🔧 Function call format issue detected")
                                continue
                                
                            if hasattr(event, 'content') and event.content:
                                if hasattr(event.content, 'parts') and event.content.parts:
                                    for part in event.content.parts:
                                        if hasattr(part, 'text') and part.text:
                                            video_analysis_result += part.text + "\n"
                        
                        if video_analysis_result.strip():
                            print("✅ Video analysis completed successfully")
                            break
                        else:
                            print(f"❌ No video analysis result on attempt {attempt + 1}")
                            
                    except Exception as e:
                        print(f"❌ Video analysis attempt {attempt + 1} failed: {str(e)}")
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 2
                            print(f"⏳ Waiting {wait_time} seconds before retry...")
                            await asyncio.sleep(wait_time)
                        else:
                            print("💥 All video analysis attempts failed")
                
                # If video analysis failed completely, create fallback analysis
                if not video_analysis_result.strip():
                    video_analysis_result = f"""FALLBACK ANALYSIS for {video_file.name}:
SUMMARY: Unable to extract and analyze video frames due to technical issues
THREATS: Manual review required - automated analysis failed
HAZARD: 5 (Unknown - requires manual inspection)
EXPOSURE: 5 (Unknown - requires manual inspection) 
VULNERABILITY: 5 (Unknown - requires manual inspection)
RISK_SCORE: 125 (Fallback score due to analysis failure)

NOTE: This video requires manual review as automated frame extraction failed."""
                    
                    print("🔄 Using fallback analysis due to video processing failure")
            
            # Create session for threat classification
            threat_session = await session_service.create_session(
                app_name="threat_classification",
                user_id="surveillance_user", 
                session_id=f"threat_{video_file.stem}"
            )
            
            print(f"✓ Created threat classification session: {threat_session.id}")
            
            # Prepare threat classification message
            threat_message = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"""SURVEILLANCE SUMMARY FOR THREAT CLASSIFICATION:

{video_analysis_result}

Please analyze the above surveillance summary and provide threat classification. Use the existing risk scores (HAZARD, EXPOSURE, VULNERABILITY, RISK_SCORE) as provided in the summary."""
                    )
                ]
            )
            
            print("🎯 Running threat classification...")
            
            # Run threat classification with retry logic
            threat_classification = ""
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    print(f"🔄 Threat classification attempt {attempt + 1}/{max_retries}")
                    
                    threat_events = threat_runner.run(
                        user_id="surveillance_user",
                        session_id=threat_session.id,
                        new_message=threat_message
                    )
                    
                    # Process threat classification events
                    for event in threat_events:
                        if hasattr(event, 'error_code') and event.error_code:
                            print(f"⚠️ Threat classification error: {event.error_code}")
                            continue
                            
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts') and event.content.parts:
                                for part in event.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        threat_classification += part.text
                    
                    if threat_classification.strip():
                        print("✅ Threat classification completed successfully")
                        break
                    else:
                        print(f"❌ No threat classification result on attempt {attempt + 1}")
                        
                except Exception as e:
                    print(f"❌ Threat classification attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"⏳ Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        print("💥 All threat classification attempts failed")
            
            # If threat classification failed, provide fallback
            if not threat_classification.strip():
                threat_classification = """THREAT_SCORE: 50
CLASSIFICATION: Normal
NOTE: Threat classification failed - manual review required"""
                print("🔄 Using fallback threat classification")
            
            # Extract and display risk score for logging
            risk_score = "Unknown"
            threat_class = "Unknown"
            
            for line in threat_classification.split('\n'):
                if line.startswith('RISK_SCORE:'):
                    risk_score = line.split(':', 1)[1].strip()
                elif line.startswith('CLASSIFICATION:'):
                    threat_class = line.split(':', 1)[1].strip()
            
            # Combine results with better formatting
            final_result = f"""=== VIDEO SURVEILLANCE ANALYSIS ===\n\n{video_analysis_result}\n\n=== THREAT CLASSIFICATION ===\n\nRISK_SCORE: {risk_score}\nCLASSIFICATION: {threat_class}"""
            
            results[video_file.name] = final_result
            
            print(f"✅ Completed: {video_file.name}")
            print(f"📊 Risk Score: {risk_score}")
            print(f"🏷️ Classification: {threat_class}")
            
        except Exception as e:
            error_msg = f"""ERROR: {str(e)}
VIDEO: {video_file.name}
TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}

FALLBACK THREAT ASSESSMENT:
THREAT_SCORE: 25
CLASSIFICATION: Normal
NOTE: Complete system failure - requires manual inspection"""
            
            results[video_file.name] = error_msg
            print(f"💥 Critical error processing {video_file.name}: {e}")
    
    # Save results with enhanced formatting
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Create summary statistics
    total_videos = len(results)
    successful_analyses = sum(1 for result in results.values() if not result.startswith("ERROR"))
    failed_analyses = total_videos - successful_analyses
    
    summary = {
        "processing_summary": {
            "total_videos": total_videos,
            "successful_analyses": successful_analyses,
            "failed_analyses": failed_analyses,
            "success_rate": f"{(successful_analyses/total_videos)*100:.1f}%" if total_videos > 0 else "0%",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        },
        "video_results": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    print(f"📈 Processing Summary:")
    print(f"   • Total Videos: {total_videos}")
    print(f"   • Successful: {successful_analyses}")
    print(f"   • Failed: {failed_analyses}")
    print(f"   • Success Rate: {summary['processing_summary']['success_rate']}")
    
    return results

def process_videos(video_directory: str = "videos", output_file: str = "src/results/video_analysis_results.json"):
    """
    Synchronous wrapper for async function with enhanced error handling
    """
    if not GOOGLE_API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        print("🔧 Please add your Google AI API key to the .env file")
        return {}
    
    try:
        return asyncio.run(process_videos_async(video_directory, output_file))
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
        return {}
    except Exception as e:
        print(f"💥 Critical system error: {e}")
        return {}

if __name__ == "__main__":
    print("🚀 Starting Video Surveillance Analysis System...")
    print("=" * 60)
    
    results = process_videos()
    
    if results:
        print("\n🎉 Video surveillance analysis completed!")
    else:
        print("\n❌ Video surveillance analysis failed or was interrupted")
