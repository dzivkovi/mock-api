### How MCP servers are normally secured

| Pattern                                             | When to use                                                      | How it works                                                                         | MCP-spec status                |
| --------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------ |
| **No auth**                                         | local dev                                                        | nothing                                                                              | ✅ allowed                      |
| **Static API-key / shared secret**                  | quick demos                                                      | `Authorization: Bearer <token>` header checked against an env var                    | ✅ allowed                      |
| **Validated JWT (Bearer)**                          | **service-to-service / client-credentials**; *no browser pop-up* | client sends Azure-issued JWT; server validates signature, issuer, audience & scopes | ✅ spec-compliant               |
| **Full OAuth 2.1 flow (code + PKCE / device-code)** | humans sign-in (VS Code, web)                                    | client discovers auth-server via MCP metadata, does normal OAuth dance               | ✅ spec-recommended but heavier |

The MCP spec simply says: **every HTTP request must carry `Authorization: Bearer <access-token>`**; the server is an OAuth 2.1 *resource server* and must validate the token ([modelcontextprotocol.io][1]).

---

## FastMCP + Azure AD (JWT validation in-process)

> **Goal:** same FastAPI process, JWTs minted by Azure AD (*client-credentials* grant, no UI).

```python
# main.py
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider

TENANT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
AUD    = "api://01234567-89ab-cdef-0123-456789abcdef"  # Application ID URI

auth = BearerAuthProvider(
    jwks_uri = f"https://login.microsoftonline.com/{TENANT}/discovery/v2.0/keys",
    issuer   = f"https://login.microsoftonline.com/{TENANT}/v2.0",
    audience = AUD,
    required_scopes=["chat.generate"]          # match the scope you exposed
)

api = FastAPI()

@api.get("/chat")                 # your existing SSE endpoint
async def chat(prompt: str): ...

mcp = FastMCP.from_fastapi(api, name="Secure-LLM", auth=auth)
api.mount("/mcp", mcp.http_app(path="/mcp"))   # MCP lives at /mcp
```

*Bear-minimum changes*: add the `BearerAuthProvider` (FastMCP 2.6+) and mount the MCP sub-app. FastMCP will:

1. **Check the JWT** on every POST `/mcp` or GET `/mcp/sse` request ([gofastmcp.com][2]).
2. Verify signature via Azure’s JWKS, issuer match, audience match, expiry, scopes.
3. Reject invalid/expired tokens with **401**; sends `WWW-Authenticate` per spec.

### Client side (Python MSAL example)

```python
from msal import ConfidentialClientApplication
app = ConfidentialClientApplication(
        client_id     = "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
        authority     = f"https://login.microsoftonline.com/{TENANT}",
        client_credential = "CLIENT_SECRET")
tok = app.acquire_token_for_client(scopes=[f"{AUD}/.default"])
hdrs = {"Authorization": f"Bearer {tok['access_token']}"}

# POST request (tool call)
requests.post("https://api.example.com/mcp", json=req, headers=hdrs, stream=True)
# SSE stream must include the *same* header
```

> **SSE quirk:** send the `Authorization` header on **both** the initial POST *and* the follow-up GET `/mcp/sse` stream; FastMCP checks each leg ([github.com][3]).

---

## If you really need **interactive** sign-in

1. Expose the API in AAD and **add an OAuth consent page**.
2. Clients (e.g. VS Code) will:

   * See a 401 + `WWW-Authenticate` pointing to `/.well-known/oauth-authorization-server`.
   * Launch the browser to Azure’s auth endpoint.
   * Receive the token and retry automatically.
     This flow is built into MCP-aware IDEs since June 12 ’25 ([code.visualstudio.com][4]).

---

## Node/TypeScript variant (same JWT rules)

```ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server";
import { createRemoteJWKSet, jwtVerify } from "jose";

const jwks = createRemoteJWKSet(
  new URL("https://login.microsoftonline.com/${TENANT}/discovery/v2.0/keys")
);
async function verify(token: string) {
  await jwtVerify(token, jwks, {
    issuer: `https://login.microsoftonline.com/${TENANT}/v2.0`,
    audience: "api://01234567-89ab-cdef-0123-456789abcdef",
  });
}

const mcp = new McpServer({ name: "secure-node" });
mcp.useAuth(async (hdr) => {           // tiny shim until SDK ships its own provider
  await verify(hdr.token);             // throw if bad
});

const transport = new StreamableHTTPServerTransport({ path: "/mcp" });
mcp.listen(transport, 8000);
```

---

### Decide which model fits

| Question                             | If answer is ***Yes*** | Suggested auth                                                                   |
| ------------------------------------ | ---------------------- | -------------------------------------------------------------------------------- |
| Only back-end services will hit MCP? | ✅                      | **Client-credentials** JWT (above)                                               |
| Humans use IDE / Browser?            | ✅                      | OAuth 2.1 **code+PKCE** (FastMCP has `OidcAuthProvider`, or front end uses MSAL) |
| Don’t want to touch AAD right now?   | ✅                      | Static API-key (shared secret) and swap later                                    |
| Need audit-grade scope / RBAC?       | ✅                      | AAD scopes + custom claims in JWT                                                |

---

### Verify everything quickly

```bash
# 1️⃣ get token
az account get-access-token \
  --resource api://01234567-89ab-cdef-0123-456789abcdef \
  --query accessToken -o tsv > token.txt

# 2️⃣ call MCP
curl -H "Authorization: Bearer $(cat token.txt)" \
     -H "Content-Type: application/json" \
     -d '{"id":"1","method":"tools.myTool","params":{"foo":"bar"}}' \
     https://api.example.com/mcp
```

If you see JSON-RPC messages back, authentication works.

---

#### Key take-aways

* MCP doesn’t invent auth—it **relies on standard OAuth 2.1** bearer tokens.
* FastMCP’s `BearerAuthProvider` means **“just validate JWTs”**—perfect for Azure AD client-credential flows.
* Put security in the *same* FastAPI process; mount `/mcp`, no proxies needed.
* For SSE, remember the header on the stream request.
* Upgrade to full OAuth later if you need interactive sign-on; the spec and VS Code already handle it.

With these pieces, your streaming endpoint is both **MCP-compliant and Azure-secured** without rewriting your existing service.

[1]: https://modelcontextprotocol.io/specification/draft/basic/authorization "Authorization - Model Context Protocol"
[2]: https://gofastmcp.com/servers/auth/bearer "Bearer Token Authentication - FastMCP"
[3]: https://github.com/modelcontextprotocol/python-sdk/issues/431 "Question: How to authorise a client with Bearer header with SSE? · Issue #431 · modelcontextprotocol/python-sdk · GitHub"
[4]: https://code.visualstudio.com/blogs/2025/06/12/full-mcp-spec-support?utm_source=chatgpt.com "The Complete MCP Experience: Full Specification Support in VS Code"
