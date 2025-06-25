Below is a focused playbook for standing-up an **external MCP proxy service** that wraps your existing streaming REST API. You’ll export the OpenAPI spec from `mock-api`, feed it to **FastMCP**, and run the proxy as an independent process (container-friendly, language-agnostic, and easy to hand off to a teammate).

---

## Key idea in one paragraph

FastMCP can bootstrap a full MCP server directly from any OpenAPI file. You point it at your upstream API with an `httpx.AsyncClient`, and it auto-generates one MCP **tool** per path/verb (including streaming ones). The proxy speaks **Streamable HTTP** and **SSE**, so Copilot, Cursor, Claude, etc. discover the tools via `tools/list` and invoke them automatically. All you write is \~40 lines of glue plus a couple of pytest checks; scaling, auth, or Dockerization can be layered on later. ([github.com][1], [gofastmcp.com][2], [modelcontextprotocol.io][3], [modelcontextprotocol.io][4])

---

## 1  Export the OpenAPI spec

```bash
python - <<'PY'
import json, pathlib, mock_api.main as m
path = pathlib.Path("openapi.json")
path.write_text(json.dumps(m.app.openapi(), indent=2))
print("Wrote", path)
PY
```

Now you have `openapi.json` beside the repo. (FastAPI exposes `.openapi()` for free.) ([gofastmcp.com][2])

---

## 2  Create the proxy project

```bash
mkdir teamcenter-mcp && cd $_
python -m venv .venv && source .venv/bin/activate
pip install "fastmcp[cli]" httpx uvicorn
```

FastMCP bundles Starlette and a CLI helper. ([github.com][1])

---

## 3  Write `server.py`

```python
# server.py  – external MCP proxy
import os, json, httpx
from fastmcp import FastMCP

# 1. where is the upstream REST API?
UPSTREAM = os.getenv("UPSTREAM_URL", "http://localhost:9000")

# 2. load the spec exported earlier
with open("openapi.json") as f:
    spec = json.load(f)

# 3. async HTTP client pointed at upstream
client = httpx.AsyncClient(base_url=UPSTREAM, timeout=None)

# 4. build the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec = spec,
    client       = client,
    name         = "Teamcenter-KB",
)

# 5. run via Streamable HTTP (plus SSE fallback on /sse)
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",   # single /mcp endpoint
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        path="/mcp"
    )
```

*What FastMCP adds*

* Parses the spec, maps every path to an MCP **tool**.
* Handles JSON-RPC, sessions, and streaming (tokens forwarded chunk-by-chunk).
* Exposes both Streamable HTTP and SSE out of the box. ([gofastmcp.com][2], [github.com][5])

---

## 4  Run & smoke-test

```bash
UPSTREAM_URL=http://localhost:9000 uvicorn server:app --port 8000
# List tools
curl -s -d '{"id":1,"method":"tools/list","params":{}}' http://localhost:8000/mcp | jq .
```

You should see each upstream route as a tool. The transport behaviour is documented in the MCP spec’s Streamable HTTP chapter. ([modelcontextprotocol.io][3], [modelcontextprotocol.io][4])

---

## 5  Add minimal pytest coverage

`tests/test_proxy.py`

```python
import pytest, httpx, asyncio, json, os, subprocess, time

BASE="http://localhost:8000/mcp"

@pytest.fixture(scope="session", autouse=True)
def proxy():
    p = subprocess.Popen(["python", "server.py"])
    time.sleep(2)          # give uvicorn time
    yield
    p.terminate()

@pytest.mark.asyncio
async def test_list():
    async with httpx.AsyncClient() as cli:
        r = await cli.post(BASE, json={"id":1,"method":"tools/list","params":{}})
    assert "result" in r.json()

@pytest.mark.asyncio
async def test_stream_chat():
    payload = {"id":2,"method":"tools/call",
               "params":{"name":"chat","arguments":{"prompt":"hello"}}}
    async with httpx.AsyncClient(timeout=None) as cli:
        async with cli.stream("POST", BASE, json=payload) as r:
            chunks = [l async for l in r.aiter_lines() if l.strip()]
    assert any("hello" in c.lower() for c in chunks)
```

Patterns borrowed from the FastAPI streaming issue and FastMCP E2E template. ([github.com][6], [dev.to][7])
For richer mocking, the `pytest_httpx` fixture can stub upstream calls. ([colin-b.github.io][8])

---

## 6  (Optionally) Dockerise and deploy

A 12-line Dockerfile suffices:

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir "fastmcp[cli]" httpx uvicorn
EXPOSE 8000
CMD ["python", "server.py"]
```

Deploy to any container host; Cloudflare Workers & Koyeb both publish step-by-step guides for remote MCP servers. ([blog.cloudflare.com][9], [koyeb.com][10])

---

## 7  Connect an IDE or agent

Add to VS Code settings (or Cursor, Claude Desktop, etc.):

```json
"mcp.servers": {
  "teamcenter": { "type": "http", "url": "http://localhost:8000/mcp" }
}
```

The LLM will now discover your tools and call them automatically—thanks to Streamable HTTP’s single endpoint. ([github.com][11])

---

## Next exploration branches

| Branch idea           | What you learn                                                                       | References                |
| --------------------- | ------------------------------------------------------------------------------------ | ------------------------- |
| **`auth-jwt`**        | Add `BearerAuthProvider` to validate Azure-issued tokens                             | FastMCP auth docs         |
| **`override-stream`** | Replace auto-generated `chat` tool with hand-tuned streaming wrapper                 | FastMCP streaming example |
| **`ts-proxy`**        | Re-implement the proxy with the TypeScript SDK using `StreamableHTTPServerTransport` | Starter repo              |

Start with the minimal proxy above, commit it to a `mcp-proxy` branch, and you’ll have a clean, demonstrable spike for tomorrow’s meeting. Good luck!

[1]: https://github.com/jlowin/fastmcp?utm_source=chatgpt.com "jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients"
[2]: https://gofastmcp.com/servers/openapi?utm_source=chatgpt.com "OpenAPI Integration - FastMCP"
[3]: https://modelcontextprotocol.io/docs/concepts/transports?utm_source=chatgpt.com "Transports - Model Context Protocol"
[4]: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports?utm_source=chatgpt.com "Transports - Model Context Protocol"
[5]: https://github.com/modelcontextprotocol/python-sdk?utm_source=chatgpt.com "The official Python SDK for Model Context Protocol servers and clients"
[6]: https://github.com/tiangolo/fastapi/issues/2006?utm_source=chatgpt.com "How to test streaming async responses with httpx AsyncClient #2006"
[7]: https://dev.to/akitana-airtanker/python-mcp-remote-server-the-dawn-of-the-streamable-http-era-with-a-minimalist-template-1o6j?utm_source=chatgpt.com "Python MCP Remote Server — The Dawn of the Streamable HTTP Era"
[8]: https://colin-b.github.io/pytest_httpx/?utm_source=chatgpt.com "pytest_httpx | pytest fixture to mock HTTPX - GitHub Pages"
[9]: https://blog.cloudflare.com/streamable-http-mcp-servers-python/?utm_source=chatgpt.com "Bringing streamable HTTP transport and Python language support ..."
[10]: https://www.koyeb.com/tutorials/deploy-remote-mcp-servers-to-koyeb-using-streamable-http-transport?utm_source=chatgpt.com "Deploy Remote MCP Servers to Koyeb using Streamable HTTP ..."
[11]: https://github.com/ferrants/mcp-streamable-http-typescript-server?utm_source=chatgpt.com "Starter for MCP Server with a Streamable HTTP Transport - GitHub"
