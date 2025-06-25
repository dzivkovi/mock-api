Copy this file into `.claude/DESIGN.md`, then tell your implementation AI:

> “Follow DESIGN.md to build and test the MCP proxy around `/stream`.”

# DESIGN.md – Teamcenter Knowledge MCP Server (Python / FastMCP)

> **Goal**  
> Wrap the existing **mock‐api** streaming REST service in a self-contained **Model Context Protocol** (MCP) server so any MCP-aware IDE / agent (Claude Desktop, VS Code Copilot, Cursor, JetBrains) can discover and call it automatically.

---

## 1 Project layout

```

mock-api/
│  openapi.json           ← exported spec (see §2-a)
│  server\_proxy.py        ← external MCP proxy  (Option B)
│  server\_inline.py       ← inline /mcp mount  (Option A)
│
tests/
│  test\_mcp.py            ← pytest smoke suite

````

---

## 2 One-time setup

### a. Export the OpenAPI spec

```bash
python - <<'PY'
import json, pathlib, mock_api.main as m
path = pathlib.Path("openapi.json")
path.write_text(json.dumps(m.app.openapi(), indent=2))
print("✅ wrote", path)
PY
````

### b. Create a virtual env & install deps

```bash
python -m venv venv && source venv/bin/activate
pip install "fastmcp[cli]" fastapi httpx uvicorn pytest sseclient-py
```

---

## 3 Pick a wrap strategy

| Strategy                      | When to choose                           | File               |
| ----------------------------- | ---------------------------------------- | ------------------ |
| **Option A – Inline route**   | Same codebase, zero extra infra          | `server_inline.py` |
| **Option B – External proxy** | Independent scaling / language isolation | `server_proxy.py`  |

Start with **Option B** (external) for the PoC; promote to inline (Option A) later if desired.

---

### Option B – External proxy (`server_proxy.py`)

```python
import os, json, httpx
from fastmcp import FastMCP

UPSTREAM = os.getenv("UPSTREAM_URL", "http://localhost:9000")

spec = json.load(open("openapi.json"))
client = httpx.AsyncClient(base_url=UPSTREAM, timeout=None)

mcp = FastMCP.from_openapi(
    openapi_spec = spec,
    client       = client,
    name         = "Teamcenter-KB",
)

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",   # also exposes /sse fallback
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        path="/mcp"
    )
```

Run locally:

```bash
UPSTREAM_URL=http://localhost:9000 python server_proxy.py
```

---

### Option A – Inline mount (`server_inline.py`)

```python
from mock_api.main import app as api
from fastmcp import FastMCP
import json, pathlib

spec = json.load(open("openapi.json"))
mcp  = FastMCP.from_openapi(spec, name="Teamcenter-KB")

api.mount("/mcp", mcp.http_app())   # original routes stay intact
```

Run:

```bash
uvicorn server_inline:api --reload --port 8000
```

---

## 4 Streaming behaviour

* If `/stream` already returns `StreamingResponse`, FastMCP streams it as-is.
* To customise, override just that tool:

```python
@mcp.tool(streaming_hint=True, name="teamcenter_chat")
async def teamcenter_chat(prompt: str) -> str:
    """Stream a chat completion from Teamcenter KB."""
    async with httpx.AsyncClient(base_url=UPSTREAM) as cli:
        async with cli.post("/stream", json={"prompt": prompt}, stream=True) as r:
            async for line in r.aiter_lines():
                mcp.ctx.stream_content(line)
    return ""
```

---

## 5 Testing (pytest)

`tests/test_mcp.py`

```python
import httpx, pytest, subprocess, time, json, os

BASE = "http://localhost:8000/mcp"

@pytest.fixture(scope="session", autouse=True)
def proxy():
    p = subprocess.Popen(["python", "server_proxy.py"])
    time.sleep(2)
    yield
    p.terminate()

@pytest.mark.asyncio
async def test_tools_list():
    async with httpx.AsyncClient() as cli:
        r = await cli.post(BASE, json={"id":1,"method":"tools/list","params":{}})
    assert any(t["name"]=="teamcenter_chat" for t in r.json()["result"])

@pytest.mark.asyncio
async def test_stream():
    payload = {"id":2,"method":"tools/call",
               "params":{"name":"teamcenter_chat","arguments":{"prompt":"hello"}}}
    async with httpx.AsyncClient(timeout=None) as cli:
        async with cli.stream("POST", BASE, json=payload) as r:
            chunks = [l async for l in r.aiter_lines() if l.strip()]
    assert chunks, "no stream received"
```

Run: `pytest -q`

---

## 6 IDE / agent integration

### Claude Desktop / Cursor

* Add server URL: `http://localhost:8000/mcp` (Streamable HTTP).
* Ask a natural question: “Find usages of `ITK_open` in Teamcenter KB.”
* Claude/Cursor auto-calls `teamcenter_chat`.

### VS Code Copilot (Insiders ≥ v1.91)

```jsonc
// settings.json
"mcp.servers": {
  "teamcenter": { "type": "http", "url": "http://localhost:8000/mcp" }
}
```

Open Copilot Chat → same query → it triggers your tool automatically.

---

## 7 (Deferred) Azure AD security

1. Expose your API in AAD, enable **client-credentials** grant.
2. Add FastMCP `BearerAuthProvider`:

```python
from fastmcp.server.auth import BearerAuthProvider
auth = BearerAuthProvider(
    jwks_uri=f"https://login.microsoftonline.com/<TENANT>/discovery/v2.0/keys",
    issuer=f"https://login.microsoftonline.com/<TENANT>/v2.0",
    audience="api://<APP-ID>",
    required_scopes=["chat.generate"],
)
mcp = FastMCP.from_openapi(spec, client=client, name="Teamcenter-KB", auth=auth)
```

Clients (CLI, IDE) send `Authorization: Bearer <token>` on both the POST and the SSE/stream requests.

---

## 8 Reference links (learn & copy)

| Topic                       | URL                                                                                                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| MCP spec (HTML)             | [https://modelcontextprotocol.dev/spec](https://modelcontextprotocol.dev/spec)                                                                         |
| MCP spec repo               | [https://github.com/modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol)                           |
| FastMCP source & README     | [https://github.com/fastmcp/fastmcp](https://github.com/fastmcp/fastmcp)                                                                               |
| FastMCP docs (RTD)          | [https://fastmcp.readthedocs.io](https://fastmcp.readthedocs.io)                                                                                       |
| Example streaming server    | [https://github.com/fastmcp/fastmcp/blob/main/examples/sse\_chat\_server.py](https://github.com/fastmcp/fastmcp/blob/main/examples/sse_chat_server.py) |
| DeepWiki MCP (multi-tool)   | [https://github.com/regenrek/deepwiki-mcp](https://github.com/regenrek/deepwiki-mcp)                                                                   |
| Sourcegraph Cody MCP thread | [https://github.com/sourcegraph/sourcegraph/discussions/57269](https://github.com/sourcegraph/sourcegraph/discussions/57269)                           |
| VS Code MCP server config   | [https://code.visualstudio.com/docs/mcp/servers](https://code.visualstudio.com/docs/mcp/servers)                                                       |

*(Trim or add links as needed for your team.)*

---

## 9 Iteration roadmap

1. **PoC** – External proxy, no auth, smoke tests.
2. **Inline** – Mount `/mcp` in main service → lower latency.
3. **Auth** – Add Azure AD JWT validation.
4. **Granular tools** – Split `teamcenter_chat` into `code_search`, `doc_search` if auto-routing proves ambiguous.
5. **Perf** – Profiling; enable HTTP/2, tune timeouts.
6. **CI** – GitHub Actions runs pytest + `fastmcp lint`.
7. **Docker** – Single image, health-check on `/mcp/ping`.

---
