from src.tools.video_loader import extract_video_frames
from src.agents.video_summarizer import video_summarizer
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
import json

async def test_video_summarizer_agent():
    print("Testing video_summarizer agent in isolation...")
    
    # Test the agent's basic properties
    print("\nAgent Properties:")
    print(f"Name: {video_summarizer.name}")
    print(f"Model: {video_summarizer.model}")
    print(f"Instruction: {video_summarizer.instruction[:100]}...")  # First 100 chars of instruction
    print(f"Tools: {[tool.__class__.__name__ for tool in video_summarizer.tools]}")
    
    # Create a runner for the agent
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=video_summarizer.name,
        agent=video_summarizer,
        session_service=session_service
    )
    
    user_id = "test_user"
    session_id = "test_session"
    # Create the session before running the agent
    await session_service.create_session(
        app_name=video_summarizer.name,
        user_id=user_id,
        session_id=session_id
    )
    
    # Extract frames from the video
    video_path = "videos/armed-robbery.mp4"
    print("\nExtracting frames from video...")
    frame_result = extract_video_frames(video_path, num_frames=3)  # Reduced to 3 frames
    if 'error' in frame_result:
        print("Error extracting frames:", frame_result['error'])
        return
    print(f"Extracted {frame_result['sampled_frames']} frames.")
    
    # Prepare the message content as JSON
    user_input = {
        "video_path": video_path,
        "frames": frame_result["frames"]
    }
    message_content = json.dumps(user_input)
    
    # Create a test message
    test_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message_content)]
    )
    
    print("\nRunning agent with video path and frames...")
    try:
        # Run the agent
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=test_message
        ):
            if event.content and event.content.parts:
                print("\nAgent Response:")
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
    except Exception as e:
        print("\nError during agent execution:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_video_summarizer_agent()) 