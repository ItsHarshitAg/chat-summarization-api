"""
Example client for the Chat Summarization API
This script shows how to interact with the API from Python.
"""

import requests
import json
from pprint import pprint

# API URL - change if deployed elsewhere
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Helper to print formatted section titles"""
    print(f"\n{'=' * 10} {title} {'=' * 10}")

def main():
    """Example workflow for using the Chat API"""
    print_section("Chat API Example Client")
    
    # Check if API is running
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code != 200:
            print("Error: API is not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {BASE_URL}")
        print("Make sure the API is running and the URL is correct")
        return
        
    print("API is running! Let's create a conversation.")
    
    # Create a conversation with initial message
    user_id = "example_user"
    conversation_id = None
    
    # 1. Create initial message
    print_section("Creating Initial Message")
    initial_message = {
        "user_id": user_id,
        "message": "Hi there! I have a question about your product."
    }
    
    resp = requests.post(f"{BASE_URL}/chats", json=initial_message)
    if resp.status_code == 201:
        print("Message created successfully!")
        result = resp.json()
        print(f"Message ID: {result['id']}")
    else:
        print(f"Error: {resp.status_code}, {resp.text}")
        return
    
    # 2. Get user's chats to find the conversation_id
    print_section("Getting User's Chats")
    resp = requests.get(f"{BASE_URL}/users/{user_id}/chats")
    if resp.status_code == 200:
        user_chats = resp.json()
        conversation_id = user_chats["chats"][0]["conversation_id"]
        print(f"Found conversation_id: {conversation_id}")
    else:
        print(f"Error: {resp.status_code}, {resp.text}")
        return
    
    # 3. Add more messages to the conversation
    print_section("Adding More Messages")
    for message_text in [
        "I'm wondering about the pricing options.",
        "Specifically, do you offer monthly plans?",
        "And is there a free trial available?"
    ]:
        message = {
            "user_id": user_id,
            "message": message_text,
            "conversation_id": conversation_id
        }
        
        resp = requests.post(f"{BASE_URL}/chats", json=message)
        if resp.status_code == 201:
            print(f"Added message: '{message_text}'")
        else:
            print(f"Error: {resp.status_code}, {resp.text}")
    
    # 4. Retrieve the entire conversation
    print_section("Retrieving Conversation")
    resp = requests.get(f"{BASE_URL}/chats/{conversation_id}")
    if resp.status_code == 200:
        conversation = resp.json()
        print(f"Retrieved {len(conversation)} messages:")
        for i, msg in enumerate(conversation, 1):
            print(f"{i}. User {msg['user_id']}: {msg['message']}")
    else:
        print(f"Error: {resp.status_code}, {resp.text}")
    
    # 5. Generate a summary
    print_section("Generating Summary")
    summary_request = {
        "conversation_id": conversation_id,
        "max_length": 30  # Short summary
    }
    
    resp = requests.post(f"{BASE_URL}/chats/summarize", json=summary_request)
    if resp.status_code == 200:
        summary = resp.json()
        print("Summary of conversation:")
        print(summary["summary"])
    else:
        print(f"Error: {resp.status_code}, {resp.text}")
    
    # 6. Demonstrate filtering and pagination
    print_section("Filtering and Pagination")
    resp = requests.get(f"{BASE_URL}/users/{user_id}/chats?limit=2&keyword=pricing")
    if resp.status_code == 200:
        filtered_results = resp.json()
        print(f"Found {filtered_results['total']} messages with 'pricing':")
        for msg in filtered_results["chats"]:
            print(f"- {msg['message']}")
    else:
        print(f"Error: {resp.status_code}, {resp.text}")
    
    print("\nThis example is complete!")
    print("Note: The test conversation has been left in the database.")
    print("You can delete it by making a DELETE request to:")
    print(f"  DELETE {BASE_URL}/chats/{conversation_id}")

if __name__ == "__main__":
    main()
