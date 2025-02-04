from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time

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
    Streaming endpoint that repeats 'search_query' three times,
    simulating SSE (Server-Sent Events) output.
    """

    def event_generator():
        # Send the query three times with slight pauses
        for _ in range(3):
            yield f"data: {search_query}\n\n"
            time.sleep(1)  # Quick pause to simulate streaming chunks

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/add_rating")
def add_rating(req: RatingRequest):
    """
    Receives a JSON payload with chat_id, search_query, and rating.
    Returns a success indicator along with the submitted data.
    """
    return {
        "status": "success",
        "received_data": req.dict()
    }
