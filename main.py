import json
import time
from enum import Enum
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


# --- Enums for choices ---
class LLMEnum(str, Enum):
    """Enumeration for supported Large Language Models."""
    GPT3_5_TURBO = "gpt-3.5-turbo"
    GPT4 = "gpt-4"
    GPT4O = "gpt-4o"


class LanguageEnum(str, Enum):
    """Enumeration for supported programming languages."""
    PYTHON = "Python"
    GO = "Go"
    CPP = "C++"
    JAVA = "Java"


# --- Pydantic Models ---
class RatingRequest(BaseModel):
    chat_id: str
    search_query: str
    rating: int


# --- FastAPI App ---
app = FastAPI(
    title="Streaming API with Enhanced Documentation",
    description="API providing streaming responses with configurable options.",
    version="1.0.0",
)


# --- Original Endpoints (preserved) ---
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


@app.get(
    "/stream",
    summary="Stream data based on a search query",
    description="Streaming endpoint that splits the given search query text into tokens "
                "and sends them in a Server-Sent Event style, with citations appended at the end.",
    response_description="A text/event-stream containing generated content chunks and citations."
)
def stream(
    search_query: str = Query(
        ...,    # Required parameter (no default)
        description="The search query text to process and stream back as tokens.",
        example="How to implement streaming in FastAPI"
    ),
    sessionID: str = Query(
        ...,    # Required parameter (no default)
        description="A unique identifier for this streaming session.",
        example="user123-20250410"
    ),
    citations: int = Query(
        5,      # Default value (replaced topNDocuments)
        description="Number of citations to include (range: 1-20).",
        ge=1,   # Minimum value
        le=20,  # Maximum value
        example=5
    ),
    llm: LLMEnum = Query(
        LLMEnum.GPT4O,  # Default to GPT-4o
        description="The large language model to use for processing.",
        example="gpt-4o"
    ),
    language: LanguageEnum = Query(
        None,   # Optional parameter (can be null)
        description="Programming language context (if applicable).",
        example="Python"
    )
):
    """
    Streaming endpoint that processes a search query and returns tokens with citations.

    Parameters:
    - **search_query**: (string, required) The text to process and stream back
    - **sessionID**: (string, required) Unique session identifier
    - **citations**: (integer, default=5) Number of citation entries (1-20)
    - **llm**: (string, default='gpt-4o') AI model to use ('gpt-3.5-turbo', 'gpt-4', 'gpt-4o')
    - **language**: (string, optional) Programming language filter ('Python', 'Go', 'C++', 'Java')

    Returns a streaming response with tokens and citations.
    """

    def event_generator():
        # Log the parameters received (optional, for debugging)
        metadata = {
            "type": "metadata",
            "data": {
                "query": search_query,
                "session": sessionID,
                "model": llm,
                "language": language,
                "citations_requested": citations
            }
        }
        yield f"data: {json.dumps(metadata)}\n\n"
        time.sleep(0.1)  # Small delay to separate metadata from content

        # Split query into tokens (every 6 characters)
        tokens = [search_query[i:i+6] for i in range(0, len(search_query), 6)]

        # Simulate streaming each token as type: response
        for token in tokens:
            chunk = {"type": "response", "data": token}
            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.1)  # quick pause to mimic streaming

        # Generate citations based on the citations parameter (renamed from topNDocuments)
        # Also incorporate the language parameter if provided
        citation_prefix = f"{language} " if language else ""

        # Use min() to respect the original limit of 10 while allowing the parameter's range to be 1-20
        citation_count = min(citations, 10)
        citations_data = [
            {"type": "citation", "data": f"{citation_prefix}Citation {i+1}: " + str(i+1) * (i+1)}
            for i in range(citation_count)
        ]

        for citation in citations_data:
            yield f"data: {json.dumps(citation)}\n\n"
            time.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# pylint: disable=unused-argument
def add_rating(req: RatingRequest):
    """
    Receives a JSON payload with chat_id, search_query, and rating.
    Returns a success indicator along with the submitted data.
    """
    return {
        "message": "Rating added successfully"
    }
