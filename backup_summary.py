"""
Local fallback summarization module that doesn't rely on external APIs.
This is used when the Gemini API is unavailable.
"""

def generate_simple_summary(conversation_text: str, max_length: int = 100) -> str:
    """
    Generate a simple summary without using external APIs.
    This is a very basic implementation that just counts messages and extracts key phrases.
    
    Args:
        conversation_text: The full conversation text
        max_length: Target length of summary in words
        
    Returns:
        A simple summary of the conversation
    """
    lines = conversation_text.strip().split('\n')
    message_count = len(lines)
    
    # Extract user IDs
    user_ids = set()
    for line in lines:
        if line.startswith("User "):
            user_id = line.split(":")[0].replace("User ", "").strip()
            user_ids.add(user_id)
    
    # Extract some key words (very basic approach)
    words = conversation_text.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Only consider words longer than 4 characters
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top 5 most frequent words
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    top_words = [word for word, _ in top_words]
    
    # Generate summary
    summary = f"This conversation consists of {message_count} messages between {len(user_ids)} participants. "
    
    if top_words:
        summary += f"Key topics appear to include: {', '.join(top_words)}. "
    
    # Add first and last message hints
    if lines:
        first_msg = lines[0].split(":", 1)[1].strip() if ":" in lines[0] else lines[0]
        summary += f"The conversation starts with '{first_msg[:30]}...' "
        
        last_msg = lines[-1].split(":", 1)[1].strip() if ":" in lines[-1] else lines[-1]
        summary += f"and ends with '{last_msg[:30]}...'"
    
    return summary
