# Chat Summarization and Insights API

A FastAPI-based REST API that processes user chat data, stores conversations in a database, and generates summaries using Google's Gemini LLM.

## Features

- ✅ Real-time chat ingestion and storage in MongoDB
- ✅ Conversation retrieval with advanced filtering by user, date, or keywords
- ✅ LLM-powered chat summarization using Google Gemini
- ✅ Optimized for heavy CRUD operations with database indexing
- ✅ Comprehensive error handling with meaningful status codes
- ✅ Fully dockerized for easy deployment

## Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - A modern, high-performance Python web framework
- **Database**: [MongoDB](https://www.mongodb.com/) - A NoSQL database for scalable applications
- **LLM Integration**: [Google Gemini](https://ai.google.dev/) - Google's multimodal AI model
- **Database Driver**: [Motor](https://motor.readthedocs.io/) - Asynchronous MongoDB driver
- **Containerization**: Docker & Docker Compose

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Google Gemini API key (get it free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Environment Setup

Create a `.env` file in the project root with the following variables:

``` bash
MONGODB_URL=mongodb://localhost:27017
GEMINI_API_KEY=your_gemini_api_key_here
```

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/chat-summarization-api.git
    cd chat-summarization-api
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file based on `.env.example`:

    ```bash
    cp .env.example .env
    ```

5. Edit the `.env` file with your MongoDB URL and Gemini API key.

## Running the Application

### Option 1: Direct Execution

```bash
uvicorn main:app --reload
```

### Option 2: Using Docker Compose (recommended)

```bash
docker-compose up -d
```

### Option 3: Separate Docker Instance

```bash
docker build -t chat-api .
docker run -p 8000:8000 --env-file .env chat-api
```

## API Endpoints

| Endpoint | Method | Description | Query Params |
|----------|--------|-------------|--------------|
| `/chats` | POST | Store chat messages | - |
| `/chats/bulk` | POST | Store multiple chat messages | - |
| `/chats/{conversation_id}` | GET | Retrieve a specific conversation | - |
| `/chats/summarize` | POST | Generate summary using LLM | - |
| `/users/{user_id}/chats` | GET | Get user's chat history | `page`, `limit`, `start_date`, `end_date`, `keyword` |
| `/chats/{conversation_id}` | DELETE | Delete a conversation | - |
| `/health` | GET | Health check | - |

## API Documentation

Once the application is running, view the interactive API documentation at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Usage Examples

### Store a Chat Message

```bash
curl -X POST "http://localhost:8000/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, how are you?",
    "metadata": {"source": "mobile"}
  }'
```

### Generate a Summary

```bash
curl -X POST "http://localhost:8000/chats/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "your_conversation_id",
    "max_length": 100
  }'
```

### Retrieve User Chat History with Filtering

```bash
curl "http://localhost:8000/users/user123/chats?page=1&limit=10&start_date=2023-01-01T00:00:00Z&keyword=hello"
```

## Performance Optimizations

The API is optimized for high-performance scenarios:

1. **Database Indexing**:
   - Compound index on `user_id` and `timestamp` for efficient user history queries
   - Text index on `message` field for keyword searching
   - Index on `conversation_id` for fast conversation lookup

2. **Asynchronous Processing**:
   - Non-blocking database operations using Motor
   - Async API requests to the Gemini LLM

3. **Connection Pooling**:
   - Configurable connection pooling for MongoDB
   - Optimized for high-throughput scenarios

4. **Bulk Operations**:
   - Batch insertion capability via `/chats/bulk` endpoint
   - Efficient processing of multiple messages

5. **Pagination**:
   - Optimized pagination for user chat history
   - Prevents memory issues with large result sets

## Testing

Run the test suite to verify functionality:

```bash
python test_api.py
```

This tests all key API endpoints including chat storage, retrieval, summarization, and deletion.

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request
