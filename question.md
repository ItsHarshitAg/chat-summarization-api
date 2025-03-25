Chat Summarization and Insights API
==============================================================

Problem Description:
Build a FastAPI-based REST API that processes user chat data, stores
conversations in a database, and generates summaries & insights using an LLMpowered summarization model.
The API should support:

- Real-time chat ingestion (store raw chat messages in a database).
- Conversation retrieval & filtering (e.g., by user, date, or keywords).
- Chat summarization (generate conversation summaries using an LLM).
- Must be optimized for heavy CRUD operations, ensuring efficient query
handling.
- Database: MongoDB (or any NoSQL preferred for scalability) or MySQL/PostgreSQL
or any of your choice.
- Implement proper error handling with meaningful status codes.
Expected Output | API Endpoints:
- Store Chat Messages (Heavy INSERT Operations) | POST /chats
- Retrieve Chats (Heavy SELECT Operations) | GET /chats/{conversation_id}
- Summarize Chat (LLM-based Summarization) | POST /chats/summarize
- Get User's Chat History (Pagination for Heavy Load Handling) | GET
/users/{user_id}/chats?page=1&limit=10
- Delete Chat (Heavy DELETE Operations) | DELETE /chats/{conversation_id}
Deployment Notes
- Deploy the API on a public server or provide a Dockerized build file.
- Store the code in a GitHub repository with clear setup instructions.
Coding Guidelines
- Follow FastAPI best practices.
- Use async database queries for scalability.
- Implement indexing & optimized queries for heavy SELECT operations.
- Provide a README.md with installation & usage details.
- Modular code with clear documentation.
- Use LLM of your choice and interact with it using APIs
