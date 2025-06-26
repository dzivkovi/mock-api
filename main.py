import json
import time
from enum import Enum
from typing import Optional
from fastapi import FastAPI, Query, Body, Header, HTTPException, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
    rating: float = Field(
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

# Security scheme
security = HTTPBearer()

# --- MCP Integration (commented out - requires standalone server) ---
# The FastMCP framework is designed to run as a standalone server
# For single-port deployment, we'd need to implement MCP protocol manually
# For now, keeping this as reference for the working standalone implementation


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
    return HTMLResponse(content="<html><body><h1>Home Page</h1></body></html>")


@app.get("/unauthorized")
def unauthorized():
    """
    Unauthorized page for non-Siemens users.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        TemplateResponse: Renders the unauthorized.html template.
    """
    return HTMLResponse(content="<html><body><h1>Unauthorized</h1><p>You are not authorized to access this resource.</p></body></html>")


@app.post("/api/login")
def api_login(
    authorization: str = Header(..., description="Authorization header"),
    x_refresh_token: Optional[str] = Header(None, alias="X-Refresh-Token")
):
    """
    API login endpoint that accepts authorization credentials.
    """
    # Mock authentication - in real implementation would validate credentials
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    return {
        "access_token": "mock_access_token_" + str(int(time.time())),
        "refresh_token": "mock_refresh_token_" + str(int(time.time())),
        "token_type": "bearer",
        "expires_in": 3600
    }


@app.get("/token")
def token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    sid: Optional[str] = Query(None, description="Session ID")
):
    """
    Token validation endpoint.
    """
    # Mock token validation
    return {
        "valid": True,
        "token": credentials.credentials,
        "sid": sid
    }


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
        description="The search query text to process and stream back as tokens."
    ),
    topNDocuments: int = Query(
        5,      # Default value
        description="Number of citations to include."
    )
):
    """
    Streaming endpoint that processes a search query and returns tokens with citations.

    Parameters:
    - **search_query**: (string, required) The text to process and stream back
    - **topNDocuments**: (integer, default=5) Number of citation entries

    Returns a streaming response with tokens and citations.
    """

    def event_generator():
        # Log the parameters received (optional, for debugging)
        metadata = {
            "type": "metadata",
            "data": {
                "query": search_query,
                "citations_requested": topNDocuments
            }
        }
        yield f"data: {json.dumps(metadata)}\n\n"
        time.sleep(0.1)  # Small delay to separate metadata from content

        # Make the esond request to the LLM (simulated here)
        search_response = search_query + ". " + """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
""" + search_query  # Simulated response

        # Split query into tokens (every 6 characters)
        tokens = [search_response[i:i+6] for i in range(0, len(search_response), 6)]

        # Simulate streaming each token as type: response
        for token in tokens:
            chunk = {"type": "response", "data": token}
            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.1)  # quick pause to mimic streaming

        # Generate citations based on the topNDocuments parameter
        citation_count = min(topNDocuments, 20)
        citations_data = [
            {"type": "citation", "data": f"Citation {i+1}: " + str(i+1) * (i+1)}
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
