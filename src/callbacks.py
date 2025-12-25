from typing import Optional

def quota_guard(callback_context, llm_request) -> Optional[str]:
    """
    Callback to prevent exceeding free tier quota limits
    Updated signature to match ADK expectations
    """
    try:
        # Rough token estimation
        request_str = str(llm_request)
        est_tokens = len(request_str) // 4
        
        TOKEN_LIMIT = 8000  # Conservative limit
        
        if est_tokens > TOKEN_LIMIT:
            return "[ABORT] Request too large - would exceed free tier quota limit."
            
    except Exception as e:
        print(f"Warning: Could not estimate tokens: {e}")
    
    return None  # Allow request to proceed
