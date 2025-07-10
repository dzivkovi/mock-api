### Recommended approach

**Mount an MCP sub-app inside your existing FastAPI service.**
FastMCP exposes a ready-made ASGI app, so you add only \~10 lines—no extra container, no reverse proxy.

---

## Step-by-step (Python 3.11+)

> **Assumptions**
>
> * You already have `app = FastAPI()` running your `/chat` SSE endpoint.
> * You want the MCP entry at `/mcp`.

1. **Install FastMCP**

   ```bash
   pip install "fastmcp[cli]"   # ≈10 MB, pulls starlette/httpx deps
   ```

2. **Wire it in** (`main.py`)

   ```python
   # --- existing imports ---
   from fastapi import FastAPI

   app = FastAPI()                              # ← your current API

   # --- NEW: add MCP ---
   from fastmcp import FastMCP

   # A. Auto-wrap every existing route  → MCP tools/resources
   mcp = FastMCP.from_fastapi(app, name="MyLLM-API")   # 🪄 one-liner :contentReference[oaicite:0]{index=0}

   # (Optional) override a streaming route if you need fine control
   # @mcp.tool(streaming_hint=True)
   # async def chat_stream(prompt: str) -> str: ...

   # B. Expose the MCP app under /mcp   (SSE + Streamable-HTTP ready)
   mcp_app = mcp.http_app(path="/mcp")                  # builds ASGI sub-app :contentReference[oaicite:1]{index=1}
   app.mount("/mcp", mcp_app)                          # final URL = /mcp/mcp
   ```

3. **Run as usual**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Tell VS Code / Copilot**

   ```jsonc
   // settings.json  (or .vscode/mcp.json)
   "mcp.servers": {
     "my-llm-api": { "type": "http", "url": "http://localhost:8000/mcp" }
   }
   ```

   Copilot now lists each FastAPI route as a callable MCP **tool**; your `/chat` stream appears automatically.

---

## Why mount inside instead of a proxy?

| In-process mount                                                                                    | Separate proxy                                                                                       |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| ✅ Single deploy & port<br>✅ No extra network hop (lower latency)<br>✅ Shares auth, logging, metrics | ✅ Can scale MCP layer independently<br>✅ Language-agnostic backend<br>✅ Clean separation of concerns |
| ❌ Coupled release cycle<br>❌ App gets heavier (adds Starlette & FastMCP)                            | ❌ Extra container / service<br>❌ Slight latency + CORS/auth plumbing                                 |

For most teams that already own the FastAPI codebase, **mounting is quicker and simpler**; you can always extract it later.

---

## Notes & tweaks

* **Custom names / exclusions** – pass `route_maps` to `FastMCP.from_fastapi` if you don’t want every endpoint exposed.
* **Auth headers** – the generated tools call your handlers **in-process**, so existing FastAPI `Depends()` auth continues to work.
* **SSE streaming** – works automatically; FastMCP detects `StreamingResponse` from your `/chat` handler and streams tokens over MCP.
* **Health-check** – `mcp.http_app()` still lets you add custom FastAPI routes (e.g., `@app.get("/health")`) outside `/mcp`.

---

### Minimal “Hello, world” template

```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()

@app.get("/ping")
def ping() -> str:
    return "pong"

# Make every FastAPI route an MCP tool
mcp = FastMCP.from_fastapi(app, name="Demo")
app.mount("/mcp", mcp.http_app(path="/mcp"))
```

`uvicorn main:app` → MCP endpoint at `http://localhost:8000/mcp`. Done.

---

**Key docs for deeper dives**

* FastAPI ↔ MCP integration guide `gofastmcp.com/deployment/asgi` ([gofastmcp.com][1])
* OpenAPI & FastAPI auto-generation overview `gofastmcp.com/servers/openapi` ([gofastmcp.com][2])

That’s all the plumbing you need—add it, deploy, and your team (and Copilot) can start calling the LLM through MCP immediately.

[1]: https://gofastmcp.com/deployment/asgi?utm_source=chatgpt.com "Integrating FastMCP in ASGI Applications"
[2]: https://gofastmcp.com/servers/openapi "OpenAPI Integration - FastMCP"
