### Short answer

**Yes — if you already have a valid Swagger / OpenAPI JSON file, FastMCP’s `FastMCP.from_openapi()` builds a working MCP server in \~10 lines.** The helper turns every operation in the spec into an MCP Tool (or Resource) and gives you a fully-typed, schema-validated wrapper out of the box. ([gofastmcp.com][1], [pypi.org][2])

---

## One-minute “hello-world” walk-through

```python
# 1. Install core libs
pip install "fastmcp[cli]" httpx sseclient-py   # sseclient only if you need SSE parsing

# 2. Bootstrap the server  (server.py)
import httpx
from fastmcp import FastMCP

spec_url   = "https://api.example.com/openapi.json"   # your Swagger file
spec       = httpx.get(spec_url).json()               # load it once
client     = httpx.AsyncClient(base_url="https://api.example.com")  # add auth headers here

mcp = FastMCP.from_openapi(
    openapi_spec = spec,
    client       = client,
    name         = "Example-LLM-API"
)

if __name__ == "__main__":
    # Pick one transport that VS Code / Copilot Agent can reach
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

Run it:

```bash
python server.py
# or: fastmcp run server.py
```

Add it to VS Code (Settings ➜ *mcp.servers*):

```jsonc
"servers": {
  "example": { "type": "http", "url": "http://localhost:8000" }
}
```

That’s it — Copilot now sees each endpoint as a callable MCP tool.

---

## Streaming endpoints (SSE) — two extra lines

`from_openapi()` issues **plain HTTP** calls by default.
If your OpenAPI operation returns an SSE stream (token chunks):

1. **Override just that route** with a custom tool:

   ```python
   from sseclient import SSEClient
   @mcp.tool(streaming_hint=True)          # lets Copilot show partial tokens
   async def chat_stream(prompt: str) -> str:
       events = SSEClient(
           client.post("/chat", json={"prompt": prompt}, stream=True)
       )
       async for ev in events:
           mcp.ctx.stream_content(ev.data)   # send chunk back immediately
       return ""                             # final return may be empty
   ```

2. Or supply a `route_map_fn` that forces that one path to a bespoke tool implementation.

Everything else in the spec stays auto-generated.

---

## When the “automatic” route is not enough

| Need                         | What to tweak                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| **Custom names / grouping**  | Pass `route_maps` or `mcp_names` to `from_openapi()` to reorganise or exclude operations. |
| **Auth / headers**           | Put tokens on the `httpx.AsyncClient` you hand to `from_openapi()`.                       |
| **Special response formats** | Post-process in a `mcp_component_fn` or manually override the generated tool.             |
| **Non-HTTP transports**      | Keep the wrapper but call your real backend over gRPC/WebSocket inside your tool code.    |

---

## Recap

* **Works out of the box** – load spec, call `FastMCP.from_openapi`, run server.
* **Streaming** – handle SSE manually in one or two wrapper functions.
* **Portability** – once wrapped, Copilot Agent, Claude Desktop, Cursor, etc. can all call your custom model exactly like Gemini or OpenAI.

That’s as close to “breeze” as it gets.

[1]: https://gofastmcp.com/servers/openapi "OpenAPI Integration - FastMCP"
[2]: https://pypi.org/project/fastmcp/2.1.0/ "fastmcp·PyPI"
