import json
import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()


# Pydantic model for /add_rating
class RatingRequest(BaseModel):
    chat_id: str
    search_query: str
    rating: int


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON indicating OK status.
    """
    return {"status": "OK"}


@app.get("/")
def login():
    """
    Mock login endpoint.
    """
    return {"message": "Login endpoint mock"}


@app.get("/home")
def home():
    """
    Mock auth redirect endpoint.
    """
    return {"message": "Home redirect mock"}


@app.get("/stream")
def stream(search_query: str, topNDocuments: int = 5, sessionID: str = "1234567890"):
    """
    Streaming endpoint that splits the given `search_query` text into tokens
    and sends them SSE-style, each line prefixed with 'data:'.
    At the end, it appends a few 'citation' lines to mimic the format legacy API.
    """

    def event_generator():
        # Split query into tokens (whitespace).
        tokens = search_query.split()

        # Simulate streaming each token as type: response
        for token in tokens:
            chunk = {"type": "response", "data": token}
            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.1)  # quick pause to mimic streaming
        citations = [{"type": "citation", "data": str(i+1) * (i+1)} for i in range(min(topNDocuments, 10))]
        for citation in citations:
            yield f"data: {json.dumps(citation)}\n\n"
            time.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/add_rating")
def add_rating(req: RatingRequest):
    """
    Receives a JSON payload with chat_id, search_query, and rating.
    Returns a success indicator along with the submitted data.
    """
    return {
        "message": "Rating added successfully"
    }
