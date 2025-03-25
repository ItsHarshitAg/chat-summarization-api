"""
Comprehensive test suite for the Chat Summarization API.
This script tests all major API endpoints and functionality.
"""
import httpx
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API URL - change if deployed elsewhere
BASE_URL = "http://localhost:8000"

async def test_api_flow():
    """Test the complete API flow with all major endpoints"""
    print("========== CHAT SUMMARIZATION API TEST SUITE ==========")
    print("Testing all major API functionality...")
    
    # Use a longer timeout for API calls
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        print("\n========== Testing Health Endpoint ==========")
        resp = await client.get(f"{BASE_URL}/health")
        print(f"Status: {resp.status_code}, Response: {resp.json()}")
        if resp.status_code != 200:
            print("ERROR: Health check failed! Exiting tests.")
            return
        
        # Create a new chat message
        print("\n========== Creating New Chat Message ==========")
        chat_data = {
            "user_id": "test_user",
            "message": "Hello, this is a test message",
            "metadata": {"source": "test_script", "version": "1.0"}
        }
        
        resp = await client.post(f"{BASE_URL}/chats", json=chat_data)
        if resp.status_code != 201:
            print(f"ERROR: Failed to create chat message: {resp.status_code}, {resp.text}")
            return
        
        result = resp.json()
        print(f"Chat created - ID: {result['id']}")
        
        # Get the conversation_id
        print("\n========== Getting Conversation ID ==========")
        resp = await client.get(f"{BASE_URL}/users/test_user/chats")
        user_chats = resp.json()
        
        if not user_chats["chats"]:
            print("ERROR: No chats found for test user")
            return
            
        conversation_id = user_chats["chats"][0]["conversation_id"]
        print(f"Found conversation_id: {conversation_id}")
        
        # Add more messages to the conversation
        print("\n========== Adding More Messages ==========")
        test_messages = [
            "How does this API work?",
            "I'm testing the conversation functionality.",
            "This is message number 3 in our test conversation.",
            "Let's see how well the summarization works with multiple messages."
        ]
        
        for message in test_messages:
            chat_data = {
                "user_id": "test_user",
                "message": message,
                "conversation_id": conversation_id
            }
            
            resp = await client.post(f"{BASE_URL}/chats", json=chat_data)
            if resp.status_code == 201:
                print(f"Added: '{message[:30]}...'")
            else:
                print(f"ERROR adding message: {resp.status_code}")
        
        # Test bulk message insertion
        print("\n========== Testing Bulk Message Insertion ==========")
        bulk_messages = [
            {"user_id": "test_user", "message": "Bulk message 1", "conversation_id": conversation_id},
            {"user_id": "test_user", "message": "Bulk message 2", "conversation_id": conversation_id},
        ]
        
        resp = await client.post(f"{BASE_URL}/chats/bulk", json=bulk_messages)
        if resp.status_code == 201:
            print(f"Successfully added {len(bulk_messages)} messages in bulk")
        else:
            print(f"ERROR with bulk insertion: {resp.status_code}")
        
        # Retrieve the conversation
        print("\n========== Retrieving Conversation ==========")
        resp = await client.get(f"{BASE_URL}/chats/{conversation_id}")
        
        if resp.status_code == 200:
            conversation = resp.json()
            print(f"Retrieved {len(conversation)} messages in conversation")
            print("First few messages:")
            for msg in conversation[:3]:
                print(f"- {msg['message'][:50]}...")
            if len(conversation) > 3:
                print(f"... and {len(conversation)-3} more messages")
        else:
            print(f"ERROR retrieving conversation: {resp.status_code}")
        
        # Generate a summary
        print("\n========== Generating Conversation Summary ==========")
        summary_data = {
            "conversation_id": conversation_id,
            "max_length": 50
        }
        
        try:
            resp = await client.post(f"{BASE_URL}/chats/summarize", json=summary_data, timeout=60.0)
            if resp.status_code == 200:
                summary = resp.json()
                print("Summary of conversation:")
                print(summary["summary"])
            else:
                print(f"ERROR generating summary: {resp.status_code}, {resp.text}")
        except httpx.TimeoutError:
            print("ERROR: Summarization request timed out. This might be due to API rate limits.")
        
        # Test pagination and filtering
        print("\n========== Testing Pagination and Filtering ==========")
        try:
            # Test basic pagination
            resp = await client.get(f"{BASE_URL}/users/test_user/chats?page=1&limit=3")
            if resp.status_code == 200:
                paginated = resp.json()
                print(f"Pagination: Got {len(paginated['chats'])} of {paginated['total']} messages with limit=3")
            
            # Test keyword filtering
            resp = await client.get(f"{BASE_URL}/users/test_user/chats?keyword=test")
            if resp.status_code == 200:
                filtered = resp.json()
                print(f"Keyword filtering: Found {filtered['total']} messages containing 'test'")
        except httpx.TimeoutError:
            print("WARNING: Pagination/filtering request timed out")
        
        # Cleanup: Delete the conversation
        print("\n========== Cleanup ==========")
        delete_choice = input("Delete test conversation? (y/n): ").lower()
        if delete_choice.startswith('y'):
            resp = await client.delete(f"{BASE_URL}/chats/{conversation_id}")
            if resp.status_code == 200:
                print(f"Successfully deleted conversation (ID: {conversation_id})")
            else:
                print(f"ERROR deleting conversation: {resp.status_code}")
        else:
            print(f"Conversation kept for review (ID: {conversation_id})")
        
        print("\n========== Test Suite Completed ==========")

if __name__ == "__main__":
    asyncio.run(test_api_flow())
