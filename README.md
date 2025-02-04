# Mock API Server

This repository contains a mock API that simulates a streaming response for search queries. It's designed to mimic the behavior of a real API that might be used in a question-answering or search system.

## Features

- Streaming response for search queries
- Simulated response and citation data
- Configurable number of top documents (citations)

## Installation

To install and run this mock API, follow these steps:

1. Clone the repository

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Start the API server:

   ```bash
   uvicorn main:app --reload
   ```

   This will start the server on `http://127.0.0.1:8000`.

## API Documentation

Once running, view the interactive API documentation at:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Usage

You can interact with the API using curl or any HTTP client. Here are some example requests:

1. Basic search query:

    ```bash
    curl -X 'GET' 'http://127.0.0.1:8000/stream?search_query=meaning%20of%20life%3F&topNDocuments=3&sessionID=12345' -H 'accept: application/json'
    ```

2. Search query with more top documents:

    ```bash
    curl -N "http://127.0.0.1:8000/stream?search_query=what%20is%20the%20meaning%20of%20life&topNDocuments=5&sessionID=12345"
    ```

3. Rating endpoint:

    ```bash
    curl -X POST "http://127.0.0.1:8000/add_rating" \
        -H "Content-Type: application/json" \
        -d '{"chat_id":"123","search_query":"test","rating":5}'
    ```

### Parameters

- `search_query`: The search query (URL-encoded)
- `topNDocuments`: The number of citation documents to return
- `sessionID`: A unique identifier for the session

### Response Format

The API returns a stream of data in the following format:

```log
data: {'type': 'response', 'data': 'word'}
data: {'type': 'citation', 'data': 'citation_id'}
```

- Response data contains individual words from the search query
- Citation data contains citation identifiers
