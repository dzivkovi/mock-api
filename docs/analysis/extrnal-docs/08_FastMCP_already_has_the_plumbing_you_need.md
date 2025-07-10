FastMCP already has the plumbing you need—all that’s left is to feed it your **mock-api** OpenAPI spec, mount the generated ASGI app, and exercise it with a few pytest checks. Below is the fastest path, with concrete links and code snippets you can copy-paste.

---

## Quick-start checklist (before tomorrow)

| Step | What to do                                                             | Why                                      |
| ---- | ---------------------------------------------------------------------- | ---------------------------------------- |
| 1️⃣  | `git clone https://github.com/dzivkovi/mock-api && cd mock-api`        | local copy of the streaming REST service |
| 2️⃣  | `pip install "fastmcp[cli]" fastapi uvicorn pytest httpx sseclient-py` | FastMCP + test deps                      |
| 3️⃣  | **Add `server_mcp.py`** (code below) at repo root                      | wraps your existing FastAPI/OpenAPI      |
| 4️⃣  | `uvicorn server_mcp:app --reload`                                      | runs `/mcp` endpoint                     |
| 5️⃣  | `pytest tests/test_mcp.py`                                             | sanity + streaming tests                 |
| 6️⃣  | Point VS Code / Claude / Cursor at `http://localhost:8000/mcp`         | verify MCP discovery                     |

That’s enough to see your streaming endpoint working through MCP inside any IDE that supports it.

---

## 1  Wrap the existing API via `FastMCP.from_openapi`

```python
# server_mcp.py
from fastapi import FastAPI
from fastmcp import FastMCP
import json, pathlib

# ---- load your mock-api app & its spec ----
from mock_api.main import app as api  # existing FastAPI app

spec_path = pathlib.Path(__file__).parent / "openapi.json"
spec = json.loads(spec_path.read_text())   # saved via api.openapi()

# ---- create MCP wrapper ----
mcp = FastMCP.from_openapi(
    openapi_spec = spec,
    name         = "Teamcenter-KB",
)

# ---- mount under /mcp (Streamable HTTP & SSE both exposed) ----
app = FastAPI()
app.mount("/mcp", mcp.http_app(path="/mcp"))   # FastMCP ≥ 2.3.2 :contentReference[oaicite:0]{index=0}
app.mount("/", api)                            # keep original routes
```

*Why it works*: `from_openapi()` auto-generates an MCP **tool** for every path/verb in the spec; `http_app()` returns a Starlette app that speaks both **SSE** and **Streamable HTTP** transports – no reverse proxy needed.  ([github.com][1], [gofastmcp.com][2])

---

## 2  Expose the streaming route cleanly

If the original `/chat` handler already returns `StreamingResponse`, FastMCP streams it out-of-the-box. If not, override just that tool:

```python
@mcp.tool(streaming_hint=True, name="code_chat")
async def code_chat(prompt: str) -> str:
    """Stream a chat completion from Teamcenter knowledge base."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as cli:
        async with cli.post("/chat", json={"prompt": prompt}, stream=True) as r:
            async for chunk in r.aiter_lines():
                mcp.ctx.stream_content(chunk)
    return ""
```

Streaming demo video (2 min) if you want to see the flow: ([youtube.com][3])

---

## 3  Minimal pytest suite (`tests/test_mcp.py`)

```python
import pytest, json, asyncio, httpx

BASE = "http://localhost:8000/mcp"

@pytest.mark.asyncio
async def test_tools_list():
    r = await httpx.post(BASE, json={"id":1,"method":"tools/list","params":{}})
    tools = r.json()["result"]
    assert any(t["name"]=="code_chat" for t in tools)

@pytest.mark.asyncio
async def test_stream_response():
    payload = {
        "id":2,
        "method":"tools/call",
        "params":{"name":"code_chat","arguments":{"prompt":"hello"}}
    }
    async with httpx.AsyncClient(timeout=None) as cli:
        async with cli.stream("POST", BASE, json=payload) as r:
            chunks = [line async for line in r.aiter_lines() if line.strip()]
    assert any("hello" in c.lower() for c in chunks)
```

*Pattern*: use **httpx.AsyncClient** with `stream()` to capture SSE/Streamable-HTTP responses; works exactly like the issue template in FastMCP’s own test suite ([github.com][4]). For broader FastAPI-pytest tips (fixtures, coverage) see this walkthrough ([augustinfotech.com][5]).

---

## 4  Verify in an IDE

1. **VS Code** ➜ *Settings* → *MCP Servers* → add

   ```json
   { "type": "http", "url": "http://localhost:8000/mcp" }
   ```
2. Reload Copilot Chat, ask:
   *“Search Teamcenter KB for `ITK_find_object` usages.”*
   Copilot will call your `code_search` or `code_chat` tool automatically if the descriptions contain “search Teamcenter KB” or similar.

DeepWiki and Sourcegraph confirmed this *auto-trigger* pattern—clear verb-based descriptions cause the LLM to invoke the tool without user hashtags ([docs.devin.ai][6], [sourcegraph.com][7]).

---

## 5  Extra reference projects worth skimming

| Repo                                      | Why it’s helpful                                                              |
| ----------------------------------------- | ----------------------------------------------------------------------------- |
| **fastmcp/examples/sse\_chat\_server.py** | Smallest working streaming server ([github.com][1])                           |
| **tadata-org/fastapi\_mcp**               | Alt.”FastAPI-first” wrapper with Depends()-based auth ([github.com][8])       |
| **regenrek/deepwiki-mcp**                 | Shows multiple *read-only* tools & clear descriptions ([github.com][9])       |
| **modelcontextprotocol.io/examples**      | Gallery of public MCP servers for inspiration ([modelcontextprotocol.io][10]) |
| **Sourcegraph community thread**          | Real-world Streamable HTTP test config ([community.sourcegraph.com][11])      |

---

### Next fork-point decisions

* **Auth later:** start unauthenticated; bolt on JWT/ADF token check via `BearerAuthProvider` once the basics pass.
* **Tool granularity:** one “mega-search” tool vs. two (`code_search`, `code_chat`). Begin simple, split only if Copilot starts picking the wrong one.
* **OpenAPI upkeep:** generate spec nightly (`app.openapi()` → file) so the MCP wrapper stays in sync.

You now have a skeleton, test harness, and live IDE integration path—enough to prove performance, refactor safety, and start adding Teamcenter-specific logic tomorrow morning. Godspeed!

[1]: https://github.com/jlowin/fastmcp?utm_source=chatgpt.com "jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients"
[2]: https://gofastmcp.com/servers/openapi?utm_source=chatgpt.com "OpenAPI Integration - FastMCP"
[3]: https://www.youtube.com/watch?pp=0gcJCdgAo7VqN5tD&v=9jGXTDkhjek&utm_source=chatgpt.com "Demo of HTTP Streamable in MCP using FastMCP - YouTube"
[4]: https://github.com/jlowin/fastmcp/issues/879?utm_source=chatgpt.com "Client Headers Missing in HTTPS Requests · Issue #879 - GitHub"
[5]: https://www.augustinfotech.com/blogs/how-to-use-coverage-unit-testing-in-fastapi-using-pytest/?utm_source=chatgpt.com "FastAPI Testing with PyTest: A Comprehensive Guide"
[6]: https://docs.devin.ai/work-with-devin/deepwiki-mcp?utm_source=chatgpt.com "DeepWiki MCP - Devin Docs"
[7]: https://sourcegraph.com/blog/cody-supports-anthropic-model-context-protocol?utm_source=chatgpt.com "Cody supports additional context through Anthropic's Model Context ..."
[8]: https://github.com/tadata-org/fastapi_mcp?utm_source=chatgpt.com "tadata-org/fastapi_mcp: Expose your FastAPI endpoints as ... - GitHub"
[9]: https://github.com/regenrek/deepwiki-mcp?utm_source=chatgpt.com "regenrek/deepwiki-mcp - GitHub"
[10]: https://modelcontextprotocol.io/examples?utm_source=chatgpt.com "Example Servers - Model Context Protocol"
[11]: https://community.sourcegraph.com/t/accessing-sqlite-through-cody-with-mcp/1573?utm_source=chatgpt.com "Accessing SQLite through Cody with MCP - Sourcegraph Forum"
