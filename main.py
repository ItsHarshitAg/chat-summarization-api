from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import httpx
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

app = FastAPI(
    title="Chat Summarization and Insights API",
    description="API for processing, storing, and analyzing chat data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = AsyncIOMotorClient(
            MONGODB_URL, 
            serverSelectionTimeoutMS=5000,
            maxPoolSize=100,  # Increased connection pool for heavy load
            minPoolSize=10,   # Maintain minimum connections
            maxIdleTimeMS=30000  # Close idle connections after 30 seconds
        )
        # Validate connection
        await app.mongodb_client.admin.command('ping')
        app.mongodb = app.mongodb_client.chat_db
        
        # Create indexes for optimized queries
        # Compound index for user+time queries which are common
        await app.mongodb.chats.create_index([("user_id", 1), ("timestamp", -1)])
        await app.mongodb.chats.create_index("conversation_id")  # For fast conversation lookup
        await app.mongodb.chats.create_index([("message", "text")])  # For text search
        
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        # We don't want to crash the app, as MongoDB might become available later

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Models
class ChatMessage(BaseModel):
    user_id: str
    message: str
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSummaryRequest(BaseModel):
    conversation_id: str
    max_length: Optional[int] = 100

class ChatResponse(BaseModel):
    id: str
    user_id: str
    message: str
    timestamp: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatPaginationResponse(BaseModel):
    chats: List[ChatResponse]
    total: int
    page: int
    limit: int
    
async def get_gemini_summary(conversation_text: str, max_length: int = 100) -> str:
    """
    Generate a summary of a conversation using Google's Gemini API.
    
    Args:
        conversation_text: The text of the conversation to summarize
        max_length: Maximum length of the summary in words
        
    Returns:
        A summary of the conversation
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        return "Error: Gemini API key not configured. Please set the GEMINI_API_KEY environment variable."
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Use the model that works based on testing
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        
        prompt = f"Summarize the following conversation in about {max_length} words:\n\n{conversation_text}"
        
        response = model.generate_content(prompt)
        
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            # Use backup summary if response format is unexpected
            from backup_summary import generate_simple_summary
            return generate_simple_summary(conversation_text, max_length)
    except Exception as e:
        # Log the error
        print(f"Gemini API error: {str(e)}")
        
        # Use fallback summarization in case of API error
        try:
            from backup_summary import generate_simple_summary
            return generate_simple_summary(conversation_text, max_length)
        except:
            return f"Error generating summary: {str(e)}"

def mongo_to_dict(obj):
    """Convert MongoDB document to dict, handling ObjectId conversion"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                obj[k] = str(v)
            elif isinstance(v, (dict, list)):
                obj[k] = mongo_to_dict(v)
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], ObjectId):
                obj[i] = str(obj[i])
            elif isinstance(obj[i], (dict, list)):
                obj[i] = mongo_to_dict(obj[i])
    return obj

# Endpoints
@app.post("/chats", response_model=Dict[str, str], status_code=201)
async def store_chat(chat: ChatMessage):
    """
    Store a new chat message in the database.
    
    - **user_id**: ID of the user sending the message
    - **message**: Content of the chat message
    - **timestamp**: ISO format timestamp (default: current time)
    - **conversation_id**: Optional ID to group messages in a conversation
    - **metadata**: Optional additional data about the message
    """
    try:
        chat_dict = chat.dict()
        if not chat_dict.get("conversation_id"):
            # Generate a new conversation ID if not provided
            chat_dict["conversation_id"] = str(ObjectId())
            
        result = await app.mongodb.chats.insert_one(chat_dict)
        return {"id": str(result.inserted_id), "message": "Chat stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store chat: {str(e)}")

@app.get("/chats/{conversation_id}", response_model=List[ChatResponse])
async def retrieve_chat(conversation_id: str):
    """
    Retrieve all messages from a specific conversation by ID.
    
    - **conversation_id**: ID of the conversation to retrieve
    """
    try:
        chats = await app.mongodb.chats.find({"conversation_id": conversation_id}).sort("timestamp", 1).to_list(length=100)
        
        if not chats:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        result = []
        for chat in chats:
            chat_dict = mongo_to_dict(chat)
            chat_dict["id"] = str(chat_dict.pop("_id"))
            result.append(chat_dict)
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat: {str(e)}")

@app.post("/chats/summarize")
async def summarize_chat(request: ChatSummaryRequest):
    """
    Generate a summary of a conversation using Google's Gemini LLM.
    
    - **conversation_id**: ID of the conversation to summarize
    - **max_length**: Maximum length of the summary in words
    """
    try:
        # Get the conversation
        chats = await app.mongodb.chats.find({"conversation_id": request.conversation_id}).sort("timestamp", 1).to_list(length=100)
        
        if not chats:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        # Format the conversation for the LLM
        conversation_text = ""
        for chat in chats:
            conversation_text += f"User {chat['user_id']}: {chat['message']}\n"
            
        # Get summary from Gemini LLM
        summary = await get_gemini_summary(conversation_text, request.max_length)
        
        # Store the summary in the database for future reference
        await app.mongodb.summaries.insert_one({
            "conversation_id": request.conversation_id,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        })
        
        return {"conversation_id": request.conversation_id, "summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize chat: {str(e)}")

@app.get("/users/{user_id}/chats", response_model=ChatPaginationResponse)
async def get_user_chats(
    user_id: str, 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    keyword: Optional[str] = None
):
    """
    Get a user's chat history with pagination and filtering options.
    
    - **user_id**: ID of the user
    - **page**: Page number
    - **limit**: Maximum number of items per page
    - **start_date**: Filter messages after this date (ISO format)
    - **end_date**: Filter messages before this date (ISO format)
    - **keyword**: Search for messages containing this keyword
    """
    try:
        # Build query with filters
        query = {"user_id": user_id}
        
        # Add date filters if provided
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
                
        # Add keyword search if provided
        if keyword:
            query["$text"] = {"$search": keyword}
            
        # Calculate pagination
        skip = (page - 1) * limit
        
        # Execute query with pagination
        chats = await app.mongodb.chats.find(query).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
        total = await app.mongodb.chats.count_documents(query)
        
        # Process results
        result = []
        for chat in chats:
            chat_dict = mongo_to_dict(chat)
            chat_dict["id"] = str(chat_dict.pop("_id"))
            result.append(chat_dict)
            
        return ChatPaginationResponse(
            chats=result,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user chats: {str(e)}")

@app.delete("/chats/{conversation_id}")
async def delete_chat(conversation_id: str):
    """
    Delete an entire conversation by ID.
    
    - **conversation_id**: ID of the conversation to delete
    """
    try:
        result = await app.mongodb.chats.delete_many({"conversation_id": conversation_id})
        if result.deleted_count:
            # Also delete any summaries
            await app.mongodb.summaries.delete_many({"conversation_id": conversation_id})
            return {"message": f"Chat deleted successfully. Removed {result.deleted_count} messages."}
        raise HTTPException(status_code=404, detail="Chat not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")

# Enhanced bulk operations for real-time chat ingestion
@app.post("/chats/bulk", response_model=Dict[str, Any], status_code=201)
async def store_chats_bulk(chats: List[ChatMessage]):
    """
    Store multiple chat messages in a single operation for improved performance.
    
    - **chats**: List of chat messages to store
    """
    try:
        chat_dicts = []
        for chat in chats:
            chat_dict = chat.dict()
            if not chat_dict.get("conversation_id"):
                chat_dict["conversation_id"] = str(ObjectId())
            chat_dicts.append(chat_dict)
            
        if not chat_dicts:
            return {"message": "No chats to insert", "count": 0}
            
        result = await app.mongodb.chats.insert_many(chat_dicts)
        return {
            "message": "Chats stored successfully", 
            "count": len(result.inserted_ids),
            "ids": [str(id) for id in result.inserted_ids]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store chats: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "healthy"}
