import json
import time
from enum import Enum
from fastapi import FastAPI, Query, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


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
    """Request model for the rating endpoint."""
    chat_id: str = Field(
        ...,  # Required field
        description="The unique identifier for the chat session being rated."
    )
    search_query: str = Field(
        ...,  # Required field
        description="The search query text that was used in this conversation.",
        example="How to implement streaming in FastAPI"  # Same example as stream route
    )
    rating: int = Field(
        ...,  # Required field
        description="The user's rating on a scale of 1-5 (1=lowest, 5=highest).",
        example=4,  # Example rating
        ge=1,  # Minimum value
        le=5   # Maximum value
    )

    class Config:
        schema_extra = {
            "example": {
                "chat_id": "user123-session456",  # Same example as sessionID in stream route
                "search_query": "How to implement streaming in FastAPI",
                "rating": 4
            }
        }


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
        example="How to implement streaming in FastAPI"  # Example value
    ),
    sessionID: str = Query(
        ...,    # Required parameter (no default)
        description="A unique identifier for this streaming session.",
        example="user123-session456"  # Example value
    ),
    topNDocuments: int = Query(
        5,      # Default value
        description="Number of citations to include (range: 1-20).",
        ge=1,   # Minimum value
        le=20,  # Maximum value
    ),
    llm: LLMEnum = Query(
        LLMEnum.GPT4O,  # Default to GPT-4o
        description="The large language model to use for processing.",
    ),
    language: LanguageEnum = Query(
        None,   # Optional parameter (can be null)
        description="Programming language context (if applicable).",
        example=LanguageEnum.PYTHON  # Example value for UI
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
                "citations_requested": topNDocuments
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

        # Generate citations based on the topNDocuments parameter
        # Also incorporate the language parameter if provided
        citation_prefix = f"{language} " if language else ""

        # Use min() to respect the original limit of 10 while allowing the parameter's range to be 1-20
        citation_count = min(topNDocuments, 20)
        citations_data = [
            {"type": "citation", "data": f"{citation_prefix}Citation {i+1}: " + str(i+1) * (i+1)}
            for i in range(citation_count)
        ]

        for citation in citations_data:
            yield f"data: {json.dumps(citation)}\n\n"
            time.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post(
    "/add_rating",
    summary="Record a user's rating for a search query",
    description="Accepts user feedback in the form of a 1-5 rating for a specific search query in a chat session.",
    response_description="Confirmation that the rating was recorded successfully."
)
def add_rating(req: RatingRequest = Body(
    ...,
    example={
        "chat_id": "user123-session456",
        "search_query": "How to implement streaming in FastAPI",
        "rating": 4
    }
)):
    """
    Records a user rating for a specific search query.

    Parameters:
    - **chat_id**: (string, required) Unique identifier for the chat session
    - **search_query**: (string, required) The search query that was rated
    - **rating**: (integer, required) Rating on a scale of 1-5

    Returns a success confirmation message.
    """
    # In a real implementation, you would store this rating in a database
    print(f"Received rating: {req.rating}/5 for query '{req.search_query}' in chat {req.chat_id}")

    # Return only the message field
    return {
        "message": "Rating added successfully"
    }
