### Core specification & reference

* **Spec repo** – Model Context Protocol:
  `https://github.com/modelcontextprotocol/modelcontextprotocol`

* **Protocol reference (HTML)** – rendered spec & message schema:
  `https://modelcontextprotocol.dev/spec`

---

### Python tooling (FastMCP)

| Purpose                                 | URL                                                                        |
| --------------------------------------- | -------------------------------------------------------------------------- |
| FastMCP source code                     | `https://github.com/fastmcp/fastmcp`                                       |
| FastMCP docs (Read-the-Docs)            | `https://fastmcp.readthedocs.io`                                           |
| “from\_openapi” how-to (README section) | `https://github.com/fastmcp/fastmcp#openapi-bootstrap`                     |
| Example server using SSE                | `https://github.com/fastmcp/fastmcp/blob/main/examples/sse_chat_server.py` |

---

### TypeScript / Node SDK

| Purpose                | URL                                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| SDK repo               | `https://github.com/modelcontextprotocol/mcp-ts-sdk`                                            |
| NPM package            | `https://www.npmjs.com/package/@modelcontextprotocol/sdk`                                       |
| Streamable-HTTP sample | `https://github.com/modelcontextprotocol/mcp-ts-sdk/tree/main/examples/express-streamable-http` |
| SSE sample             | `https://github.com/modelcontextprotocol/mcp-ts-sdk/tree/main/examples/sse-server`              |

---

### Sample servers that wrap other LLM APIs

| Wrapper                                                      | URL                                                    |
| ------------------------------------------------------------ | ------------------------------------------------------ |
| **Any-Chat-Completions** (forwarder to any OpenAI-style API) | `https://github.com/mcp-examples/any-chat-completions` |
| Claude bridge                                                | `https://github.com/mcp-examples/claude-mcp-server`    |
| Gemini bridge                                                | `https://github.com/mcp-examples/gemini-mcp-server`    |

---

### VS Code integration docs

* **Configuring MCP servers in VS Code**
  `https://code.visualstudio.com/docs/mcp/servers`

* **Copilot agent mode & MCP tools**
  `https://code.visualstudio.com/blogs/2025/03/20/copilot-agent-mcp`

---

### Blog posts / tutorials

| Topic                                                     | URL                                                                  |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| Intro to MCP (official blog)                              | `https://modelcontextprotocol.dev/blog/introducing-mcp`              |
| “Building an MCP server in 10 minutes” (FastMCP tutorial) | `https://fastmcp.readthedocs.io/en/latest/tutorials/quickstart.html` |
| “Exposing your OpenAPI service as MCP”                    | `https://fastmcp.readthedocs.io/en/latest/tutorials/openapi.html`    |

---

**Tip:** Start by cloning the FastMCP repo and the *Any-Chat-Completions* server—those two provide 90 % of the patterns you’ll reuse.
