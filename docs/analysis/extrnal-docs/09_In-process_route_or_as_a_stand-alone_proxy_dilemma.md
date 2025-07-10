Adding MCP to an existing service can be done **either** as an *in-process route* or as a *stand-alone proxy*.  Most teams simply **mount a new `/mcp` path inside the FastAPI app they already ship**, because it’s one file and zero extra infra; use a proxy only when you need independent scaling or language isolation.

---

## Option 1 – Mount an `/mcp` route inside your FastAPI app

| What you do                     | How                                                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 🟢 **Keep the current process** | Import your FastAPI app, call `FastMCP.from_openapi(app.openapi())`, then `app.mount("/mcp", mcp.http_app())`. |
| 🟢 **No extra network hop**     | The wrapper calls your own Python functions directly; latency stays \~ the same.                               |
| 🟢 **Shares auth, logging**     | Existing middleware (JWT, AAD) still runs because requests come through the same ASGI stack.                   |

> The `fastapi-mcp` helper even does the mount in one line – `FastApiMCP(app).mount()` – and auto-generates the MCP schema.

---

## Option 2 – Run a separate “proxy” MCP service

| What you do                              | How                                                                                                                                                       |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔵 **Spin up a new process / container** | Use `FastMCP.from_openapi(spec)` (or the TypeScript SDK) **without** importing your FastAPI code; forward HTTP to `http://upstream/chat` etc.             |
| 🔵 **Decouple release cycles**           | You can upgrade the MCP layer or SDK without touching the main API.                                                                                       |
| 🔵 **Scale independently / polyglot**    | Handy if the core API is Java/Go but you want a Python or Node MCP layer, or if you plan heavy prompt-engineering logic that may need its own CPU budget. |
| 🔴 **Adds latency & ops**                | One more service to deploy, health-check, secure, and monitor.                                                                                            |

---

## Which one should *you* use?

Because your **mock-api** is already FastAPI **and** you care about minimum effort tomorrow, choose **Option 1**:

```python
from mock_api.main import app as api
from fastmcp import FastMCP
import json, pathlib

spec = json.loads((pathlib.Path(__file__).parent/"openapi.json").read_text())
mcp  = FastMCP.from_openapi(openapi_spec=spec, name="Teamcenter-KB")
api.mount("/mcp", mcp.http_app())          # new route, same server
```

This pattern is endorsed in the official *ASGI integration* guide and multiple community examples; projects like Qdrant’s server and Sourcegraph’s internal demos do the same when their API is Python-based.

---

## When a proxy *does* make sense

* Your core API is **non-Python** and embedding the MCP SDK would add a big runtime.
* You need to **rate-limit or cache** MCP traffic separately.
* You want to **stage a rewrite** – keep the old service but experiment with new tools/prompt logic in the proxy.

Teams like AWS’s MCP demos use a proxy so they can combine Lambda + API Gateway while the original backend stays untouched.

---

## Next concrete steps

1. **Generate the spec**: `python -c "import mock_api.main as m, json, pathlib, sys; pathlib.Path('openapi.json').write_text(json.dumps(m.app.openapi()))"`
2. **Drop in the mount snippet** above and run `uvicorn mock_api.main:app`.
3. **Hit `/mcp`** with `tools/list` to confirm the AI can see your new tools.
4. **Add pytest streaming checks** (see earlier answer) to guard regressions.

Start with the in-process route; you can always lift it out to a proxy later if performance or organisational boundaries demand it.
