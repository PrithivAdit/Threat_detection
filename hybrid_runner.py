#!/usr/bin/env python3
"""
Hybrid Video Surveillance Runner - Combines Simple API + ADK Agents
"""

import json
import os
import pathlib
from enhanced_video_analzyer import get_sequential_description
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.agents.workflow import root_agent
from src.settings import GOOGLE_API_KEY
from google.genai import types
import asyncio

async def analyze_video_hybrid(video_path):
    """Hybrid approach: Simple API for description + ADK for classification"""
    
    print(f"🎯 HYBRID ANALYSIS: {os.path.basename(video_path)}")
    print("="*60)
    
    # Step 1: Get detailed sequential description (Simple API - More frames)
    print("📹 Step 1: Extracting sequential description...")
    video_description = get_sequential_description(video_path)
    
    if video_description.startswith("ERROR"):
        return {"error": video_description}
    
    print("✅ Sequential description extracted")
    print(f"Description length: {len(video_description)} characters")
    
    # Step 2: Use ADK for threat classification (Structured analysis)
    print("\n🤖 Step 2: Running ADK threat classification...")
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="hybrid_surveillance",
        session_service=session_service
    )
    
    try:
        # Create session
        session = await session_service.create_session(
            app_name="hybrid_surveillance",
            user_id="surveillance_user",
            session_id=f"hybrid_{os.path.basename(video_path)}"
        )
        
        print(f"✅ Created ADK session: {session.id}")
        
        # Create message with video description
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=f"Analyze this surveillance video description:\n\n{video_description}")]
        )
        
        # Run ADK workflow
        events = runner.run(
            user_id="surveillance_user",
            session_id=session.id,
            new_message=user_message
        )
        
        # Extract classification result
        classification_result = ""
        for event in events:
            if hasattr(event, 'content') and event.content:
                classification_result += str(event.content)
        
        print("✅ ADK classification completed")
        
        return {
            "video_file": os.path.basename(video_path),
            "sequential_description": video_description,
            "adk_classification": classification_result,
            "approach": "hybrid_simple_api_plus_adk",
            "success": True
        }
        
    except Exception as e:
        return {
            "video_file": os.path.basename(video_path),
            "error": f"ADK processing failed: {str(e)}",
            "sequential_description": video_description,
            "success": False
        }

def process_videos_hybrid(video_directory="videos"):
    """Process all videos using hybrid approach"""
    
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not found in .env file")
        return
    
    video_path = pathlib.Path(video_directory)
    video_files = list(video_path.glob("*.mp4")) + list(video_path.glob("*.avi")) + list(video_path.glob("*.mov"))
    
    if not video_files:
        print(f"No video files found in {video_directory}")
        return
    
    results = {}
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n{'='*60}")
        print(f"PROCESSING {i}/{len(video_files)}: {video_file.name}")
        print(f"{'='*60}")
        
        result = asyncio.run(analyze_video_hybrid(str(video_file)))
        results[video_file.name] = result
        
        if result.get("success"):
            print(f"\n✅ COMPLETED: {video_file.name}")
        else:
            print(f"\n❌ FAILED: {video_file.name}")
    
    # Save results
    os.makedirs("app/results", exist_ok=True)
    output_file = "app/results/hybrid_analysis_results.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎯 RESULTS SAVED: {output_file}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("HYBRID ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    for video_name, result in results.items():
        print(f"\n📹 {video_name}:")
        if result.get("success"):
            print("✅ Status: SUCCESS")
            if "adk_classification" in result:
                classification = result["adk_classification"]
                # Extract TOTAL RISK SCORE
                risk_score = None
                for line in classification.split('\n'):
                    if 'RISK_SCORE:' in line:
                        risk_score = line.split('RISK_SCORE:')[1].split()[0].strip()
                        break
                if risk_score:
                    print(f"🎯 TOTAL RISK SCORE: {risk_score}")
                # Extract CLASSIFICATION
                threat_type = None
                for line in classification.split('\n'):
                    if 'CLASSIFICATION:' in line:
                        threat_type = line.split('CLASSIFICATION:')[1].strip()
                        break
                if threat_type:
                    print(f"🏷️  THREAT TYPE: {threat_type}")
                # Print END SUMMARY
                print("\nEND SUMMARY:")
                # Try to extract summary from classification
                summary = None
                for line in classification.split('\n'):
                    if line.strip().startswith('SUMMARY:'):
                        summary = line.strip()[len('SUMMARY:'):].strip()
                        break
                if summary:
                    print(summary)
                else:
                    print("No summary available.")
                # Add threat assessment
                if threat_type and threat_type.lower() != 'normal':
                    print(f"\n⚠️  This video is classified as a THREAT: {threat_type}")
                else:
                    print("\n✅ This video is NOT a threat (Normal)")
        else:
            print("❌ Status: FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    print("🚀 STARTING HYBRID VIDEO SURVEILLANCE ANALYSIS")
    print("Approach: Simple API (8 frames) + ADK Agents (classification)")
    print("="*60)
    
    results = process_videos_hybrid()
    
    if results:
        print(f"\n🎉 ANALYSIS COMPLETE! Processed {len(results)} videos")
    else:
        print("\n❌ No videos processed")
