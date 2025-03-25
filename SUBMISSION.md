# Chat Summarization and Insights API - Submission

## Project Overview

This project implements a FastAPI-based REST API for processing, storing, and analyzing chat data with LLM-powered summarization using Google's Gemini API. The application follows the requirements specified in the assignment and includes all requested endpoints with proper error handling, pagination, and filtering capabilities.

## Key Features Implemented

1. **RESTful API** with FastAPI implementing all required endpoints:
   - `POST /chats` - Store chat messages
   - `GET /chats/{conversation_id}` - Retrieve conversation
   - `POST /chats/summarize` - Summarize conversations with Gemini
   - `GET /users/{user_id}/chats` - Get user's chat history with pagination
   - `DELETE /chats/{conversation_id}` - Delete conversations

2. **Database Integration** with MongoDB using asynchronous queries via Motor

3. **Performance Optimizations**:
   - Indexes for improved query performance
   - Pagination for high-volume data retrieval
   - Asynchronous database operations

4. **Filtering Capabilities**:
   - Filter by date range
   - Filter by keywords with text search
   - Sort options

5. **LLM Integration** with Google's Gemini for chat summarization

6. **Docker and Docker Compose** configuration for easy deployment

7. **Testing** with included test script

## Running the Application

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

### Docker Deployment

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Using just Docker
docker build -t chat-api .
docker run -p 8000:8000 -e MONGODB_URL=mongodb://host.docker.internal:27017 -e GEMINI_API_KEY=your_key_here chat-api
```

## Testing

1. Run the included test script:

    ```bash
    python test_api.py
    ```

2. Or use the client example:

    ```bash
    python client_example.py
    ```

3. API documentation is available at:

    ``` bash
    http://localhost:8000/docs
    ```

## Design Decisions

1. **MongoDB** was chosen for its flexibility with unstructured data and built-in text search capabilities.

2. **Async Operations** were implemented throughout to handle high load scenarios.

3. **Gemini API** was selected for summarization due to its free availability and strong performance.

4. **Comprehensive Error Handling** with specific error messages and status codes.

5. **Environment-based Configuration** to support different deployment environments.

## Future Improvements

1. Implement authentication and authorization
2. Add comprehensive unit and integration tests
3. Add rate limiting for public-facing deployments
4. Implement WebSockets for real-time chat functionality
5. Add caching for frequently accessed data
