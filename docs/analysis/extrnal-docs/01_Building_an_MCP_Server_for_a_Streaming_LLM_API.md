Thanks, that's clear. I’ll research how to wrap a custom SSE-based streaming REST API into an MCP server using Python (ideally FastMCP), as well as whether there's support or tooling to build equivalent MCP plugins from GitHub Copilot ChatParticipants (TypeScript). I’ll also look at how developers are exposing external LLMs like Gemini through MCP servers.

I’ll get back to you with concrete options, toolkits, and examples for both Python and Node.js/TypeScript, as well as practical steps to prototype or deploy your solution.


# Building an MCP Server for a Streaming LLM API

Integrating your streaming SSE-based LLM endpoint into VS Code’s **Model Context Protocol (MCP)** ecosystem can be done via two main paths. Below, we outline both approaches – using Python with **FastMCP** and using **Node.js/TypeScript** – along with tips from existing MCP solutions and guidance on transitioning from VS Code ChatParticipants to MCP.

## Option 1: Python + FastMCP (Rapid Prototyping)

**FastMCP** is a high-level Python framework for MCP, designed for quick development. It’s part of the official MCP Python SDK and offers many conveniences for production-ready servers. To wrap your SSE streaming API:

1. **Install FastMCP**: Install the `mcp` package (with CLI extras) via pip: `pip install "mcp[cli]"`. This provides the `FastMCP` class for server creation.
2. **Define MCP Server and Tools**: In a Python script, import and initialize a server. Then register a *tool* that calls your LLM API. For example:

   ```python
   from mcp.server.fastmcp import FastMCP
   mcp = FastMCP("My LLM Server")

   @mcp.tool()
   def chat_complete(prompt: str) -> str:
       # Call your SSE API (synchronously or asynchronously)
       response = ...  # e.g., requests or aiohttp to your SSE endpoint
       return response_text
   ```

   Each `@mcp.tool` function should accept input (e.g. a prompt) and return the result (e.g. the model’s completion text). FastMCP will expose this as an MCP tool that the agent can invoke.
3. **Handle Streaming Output**: MCP is built on streaming. Under the hood, tool responses can stream token-by-token to the client via SSE. If using FastMCP’s SSE transport, you can simply return the final concatenated output – FastMCP handles streaming it over SSE. (FastMCP’s design aligns with SSE clients, ensuring compatibility with token streams.)
4. **Run the Server**: Choose a transport. For local testing you can use STDIO, but for use in VS Code or remote, run an HTTP server:

   * **SSE transport** (Server-Sent Events): `mcp.run(transport="sse", host="0.0.0.0", port=8000)`. This starts an SSE endpoint (usually at `/sse`) that VS Code can connect to.
   * **Streamable HTTP**: `mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/mcp")`. VS Code supports streamable HTTP as well (it will try HTTP and fall back to SSE).
5. **Configure VS Code**: In VS Code’s MCP settings (e.g. in `.vscode/mcp.json` or user settings), add your server. For example:

   ```json
   {
     "servers": {
       "myCustomLLM": {
         "type": "http", 
         "url": "http://localhost:8000"
       }
     }
   }
   ```

   Use `"type": "http"` (VS Code will try HTTP or SSE automatically for network servers). Now your custom LLM appears as a tool in Copilot agent mode.

**FastMCP features:** FastMCP provides advanced shortcuts. Notably, you can auto-generate an MCP server from an OpenAPI spec or FastAPI app using `FastMCP.from_openapi()` or `FastMCP.from_fastapi()`. If your SSE REST API has an OpenAPI definition, this can rapidly scaffold tools for each endpoint ****. FastMCP also supports authentication, server composition, and more, which can be useful as you productionize your solution.

## Option 2: Node.js/TypeScript + MCP SDK (VS Code Extension Approach)

If you prefer TypeScript (and perhaps want to leverage existing extension code), the official **TypeScript MCP SDK** is available. You can build a Node-based MCP server as follows:

1. **Set Up Project**: Install the SDK with `npm install @modelcontextprotocol/sdk`. Initialize an MCP server in a Node script:

   ```js
   import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
   import { StreamableHTTPServerTransport, SSEServerTransport, StdioServerTransport } from "@modelcontextprotocol/sdk/server";

   const server = new McpServer({ name: "my-llm-server", version: "1.0.0" });
   ```
2. **Register Tools**: Use `server.registerTool` to define a tool that calls your SSE API. For example:

   ```js
   server.registerTool(
     "chatComplete",
     { title: "Chat Completion", description: "Call custom LLM endpoint", inputSchema: { prompt: z.string() } },
     async ({ prompt }) => {
       const res = await fetch(MY_API_URL, { method: "POST", body: JSON.stringify({ prompt }) });
       // Read streaming response and accumulate (or yield partial content if supported)
       const text = await res.text();
       return { content: [{ type: "text", text }] };
     }
   );
   ```

   This defines a tool named “chatComplete” that the agent can invoke. The return format uses an array of content parts (here just one text block) as per the MCP spec.
3. **Implement the Transport**: For a standalone HTTP server, the SDK provides a sample pattern for **Streamable HTTP**. Essentially, you create an Express app that handles a POST route (for client->server messages) and an SSE GET route (for server->client events) using the SDK’s transports. For example, the SDK docs show setting up an Express app with `StreamableHTTPServerTransport` on a `/mcp` endpoint. Alternatively, for SSE specifically, you can use `SSEServerTransport`: the approach (as seen in MCP Lab code) is to accept `GET /sse`, create a new `SSEServerTransport(fullUrl, res)` and connect the server. The key is to hold transports per session and forward requests and events appropriately.

   * Simpler: use the **“stateless” Streamable HTTP** approach from the SDK, which uses a single `/mcp` route for both request and response streams and manages session headers.
   * For local development or integration inside an extension process, you could use STDIO (similar to the Python approach) by running the server with a `StdioServerTransport` and configuring the VS Code server entry with `"type": "stdio", "command": "node", "args": ["server.js"]`.
4. **Run & Configure**: Run your Node script (or package it as an npm tool). Then add it to VS Code’s MCP config. For streamable HTTP/SSE, use the `"type": "http"` and provide the base URL as shown above. For stdio, list the command and args as in the Perplexity example (e.g. using `npx` or a direct node path).

**Tip:** If you have an existing VS Code *ChatParticipant* extension, you can repurpose its logic here. Likely, that extension was forwarding requests to your SSE API using VS Code’s Chat API. You can now move that request logic into an MCP tool. The TypeScript SDK lets you produce streaming responses similarly to how the Chat API’s `ResponseStream` works, but with the benefit that the tool can be invoked in agent mode automatically. Essentially, instead of an in-extension `@participant`, you’ll have an external tool the agent can call.

## Examples of Third-Party LLM MCP Servers

You’re not alone in wanting to plug in alternate LLMs – the community has created many MCP servers for various models:

* **“Any Chat Completions” Server:** An open-source MCP server that exposes a single `chat` tool to relay prompts to any OpenAI-compatible Chat Completions API (e.g. OpenAI, Perplexity, xAI, etc.). It’s written in TypeScript and simply forwards the user’s question to the configured API (using env vars for API key, base URL, model name, etc.). This is a great template for how to structure an MCP tool around a streaming chat API – effectively, it treats the third-party LLM as a tool that the main assistant can call when needed.
* **FastMCP OpenAPI Generation:** FastMCP’s ability to **generate servers from REST specs** means you could scaffold a server around a third-party model’s API very quickly. For instance, if an LLM has an OpenAPI (some do), `FastMCP.from_openapi(spec_url)` can create a server with tools for each operation.
* **APIWeaver:** This project dynamically creates MCP servers from generic API configurations, enabling quick integration of any REST or GraphQL service as an MCP tool. If your LLM API is not OpenAI-like, using a tool like APIWeaver (or writing a small glue layer) could save time.
* **Claude/Gemini Integrations:** Anthropic’s Claude and Google’s Gemini have been integrated via MCP by the community. For example, one community server bridges Claude with Google’s Gemini, letting Claude delegate tasks to Gemini via MCP. The general pattern is the same: the MCP server accepts a request (e.g. “analyze code with Gemini”) and calls the external model’s API, then returns the analysis to the primary assistant. In VS Code’s context, GitHub has even documented using Claude models in Copilot Chat natively, but if you have API access to a model, you can emulate that by creating your own MCP interface.

In short, exposing third-party LLMs usually involves writing a lightweight MCP server that *calls the model’s API and streams back the response*. This is exactly what you’ll be doing with your custom SSE endpoint. The **MCP official server repository** and curated lists are great places to see examples (e.g. servers for HuggingFace models, Azure OpenAI, etc.) and even reuse code. For instance, the Any Chat Completions server above can be installed via `npx` and configured to point at a new base URL – if your API closely mirrors OpenAI’s, this could be a plug-and-play solution.

## From VS Code ChatParticipant to MCP

VS Code’s Chat Extensions API allowed adding custom **chat participants** – essentially domain-specific responders within the chat UI. If you built a TypeScript ChatParticipant (e.g., an `@myModel` that streams replies via your API), converting it to MCP is advantageous for a few reasons:

* **Broader Availability:** MCP servers aren’t limited to VS Code’s Ask Mode; they can be used in **Agent Mode** (automatically invoked by Copilot when relevant) and even in other MCP-compatible clients like Claude Desktop or Cursor. Your AI becomes a first-class tool in the ecosystem.
* **Simplicity of Integration:** Rather than maintaining VS Code extension lifecycle and UI, an MCP server is a standalone service. You just ensure the server is running (or configured to auto-start via the MCP JSON), and VS Code will handle connecting to it. For example, with a proper config, VS Code can launch an MCP server via a simple command (even using `npx` to run your Node tool).
* **Reuse of Logic:** You can reuse your extension’s core logic. If your extension forwarded the user query to an API and streamed the answer, that logic becomes the implementation of your MCP tool. The difference is you return the answer through MCP’s protocol instead of rendering directly in VS Code. Given that MCP messages can include markdown and other rich content, you won’t lose much fidelity.

**Guidance:** Extract the API-calling code from your extension and put it in a tool function (as shown in the Node approach above). If your extension used VS Code’s `LanguageModel` API to stream, now you’ll use the MCP SDK’s tool response to stream. Once done, you can retire the ChatParticipant extension or even transform it into a simple wrapper that starts your MCP server in the background.

---

By following these steps, you can have a working MCP server that exposes your streaming LLM API in VS Code’s Copilot agent environment. Whether you choose Python or TypeScript, there are robust tools and examples to jump-start the process. For rapid prototyping, **FastMCP** in Python offers quick scaffolding (even generating servers from specs), while the **TypeScript SDK** gives you fine control and the ability to integrate with existing code. Both approaches align with how others are integrating models like Claude, Gemini, and more via MCP – usually by creating a single-tool server that *relays chat completions* to the external model. With this in place, your custom SSE endpoint can be used just like any other Copilot tool or model, greatly expanding your Copilot’s capabilities. Good luck with building your MCP server!

**Sources:**

* GitHub Copilot & VS Code documentation on MCP and Chat extensions
* *FastMCP* project documentation and README (features, transports, usage)
* *Any Chat Completions* MCP server (PyroPrompts) – example of bridging OpenAI-style APIs via MCP
* VS Code *mcp.json* configuration guide (server types and setup)
* Anthropic/Community resources on MCP for external models (Claude, etc.)
