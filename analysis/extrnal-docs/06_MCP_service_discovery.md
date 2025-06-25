In MCP, **the AI agent “discovers” your server, reads a structured list of tools, and then decides when to call them based only on the natural-language descriptions and JSON-Schema you publish.** You rarely need extra wiring beyond a good definition; if you want deterministic control you can still force calls. Below is the mechanics and the levers you can tweak.

## 1  How discovery works

| Step            | What happens                                                                                                                                                          | Spec / docs                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1. Handshake    | Client sends `initialize`, server replies with protocol/version info                                                                                                  | ([stytch.com][1])                                            |
| 2. Tool list    | Client sends `{ "method": "tools/list" }`, server returns an array of tool definitions                                                                                | ([modelcontextprotocol.io][2], [modelcontextprotocol.io][3]) |
| 3. Agent prompt | The host (e.g. VS Code Copilot) feeds each tool’s **name, description and JSON-Schema** into the model’s system prompt or the model-vendor’s “function calling” field | ([philschmid.de][4], [stytch.com][5])                        |
| 4. Decision     | When user intent matches a tool description, the LLM emits a JSON-RPC call; host turns that into `tools/call`                                                         | ([quickchat.ai][6], [nccgroup.com][7])                       |
| 5. Result loop  | Host forwards the tool result back into the conversation; model continues                                                                                             | ([stytch.com][5])                                            |

## 2  What to publish in a tool definition

```python
@mcp.tool(
    name="chat_stream",
    description="Stream a chat completion from ACME-LLM. \
Use when the user wants a conversational answer from the ACME engine.",
    input_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "User’s query"},
            "max_tokens": {"type": "integer", "default": 1024}
        },
        "required": ["prompt"]
    },
    annotations={
        "title": "ACME Chat",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
```

**Key fields**

* **`name`** – unique; keep it verb-like (`chat_stream`, `analyze_code`).
* **`description`** – plain English *“Use when…”* guidance; this is what the LLM matches on.([modelcontextprotocol.io][3], [modelcontextprotocol.io][3])
* **`inputSchema`** – JSON Schema tells the agent which arguments it can supply.([modelcontextprotocol.io][3])
* **`annotations`** – optional hints for UX (read-only, destructive, etc.).([modelcontextprotocol.io][3])

### Writing effective descriptions

* **Start with an action verb** (“Generate”, “Update”, “Search”).
* **Include the trigger phrase**: “Use when the user asks …”.
* **Mention limits**: rate-limits, max tokens.
* **Add an example** in the description if it avoids ambiguity. These tips map directly to best-practice notes in the spec.([modelcontextprotocol.io][3], [modelcontextprotocol.io][3])

## 3  How the LLM decides (auto vs. explicit)

| Mode               | How to trigger                                                                                                                             | When useful                         | Reference                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | ------------------------------------------------ |
| **Auto (default)** | Leave `tool_choice` = `auto` (VS Code/Claude/OpenAI do this automatically). The model picks a tool if description/schema match the request | Normal usage                        | ([devblogs.microsoft.com][8], [quickchat.ai][6]) |
| **Forced**         | Host sets `tool_choice` = `"chat_stream"` or similar when sending the prompt                                                               | Deterministic flows, tests          | ([learn.microsoft.com][9])                       |
| **User nudge**     | In Copilot chat, type `#` and select the tool from the wrench menu—or type `#chat_stream` inline                                           | When you want to override the model | ([reddit.com][10])                               |

> **Bottom line:** if your descriptions are clear, the agent will pick the right tool without any extra code.

## 4  Testing that discovery works

```bash
# 1. List tools
curl -H "Authorization: Bearer $TOKEN" \
     -d '{"id":1,"method":"tools/list","params":{}}' \
     https://api.example.com/mcp

# 2. Simulate a call
curl -H "Authorization: Bearer $TOKEN" \
     -d '{"id":2,"method":"tools/call","params":{"name":"chat_stream","arguments":{"prompt":"hi"}}}' \
     https://api.example.com/mcp
```

If the list shows your tool with the expected description and the call succeeds, Copilot/Claude etc. will behave the same way.

## 5  Advanced levers

| Need                       | Tweak                                                                                                                                                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Discourage risky calls** | Set `destructiveHint: true`; hosts will ask for explicit user approval.([modelcontextprotocol.io][3])                                                                                                                           |
| **Document cost**          | Add `"pricing_cents_per_1000_tokens": 3` inside `annotations`—some hosts display that.                                                                                                                                          |
| **Hide internal tools**    | Omit them from `tools/list` result or expose them only via an `"internal": true` annotation if your SDK supports it.                                                                                                            |
| **Dynamic availability**   | Return fewer tools to unauthenticated users; send `notifications/tools/list_changed` if the set changes.([modelcontextprotocol.io][2])                                                                                          |
| **Agent frameworks**       | LangChain, Semantic Kernel, Azure Foundry all auto-convert MCP tools into their internal “functions,” so a good description is still the only routing signal. ([devblogs.microsoft.com][11], [techcommunity.microsoft.com][12]) |

---

### Recap

1. **Expose tools** with clear descriptions & JSON Schema.
2. **Discovery** (`tools/list`) is automatic; hosts feed that into the LLM.
3. The **model decides** based on your description, or you can force with `tool_choice` or `#`.
4. Use annotations to hint read-only vs. destructive actions.
   Do this, and your new MCP layer will be invoked naturally whenever it’s the best way to satisfy the user’s request.

[1]: https://stytch.com/blog/model-context-protocol-introduction/?utm_source=chatgpt.com "Model Context Protocol (MCP): A comprehensive introduction for ..."
[2]: https://modelcontextprotocol.io/docs/concepts/tools?utm_source=chatgpt.com "Tools - Model Context Protocol"
[3]: https://modelcontextprotocol.io/docs/concepts/tools "Tools - Model Context Protocol"
[4]: https://www.philschmid.de/mcp-introduction?utm_source=chatgpt.com "Model Context Protocol (MCP) an overview - Philschmid"
[5]: https://stytch.com/blog/model-context-protocol-introduction/ "Model Context Protocol (MCP): A comprehensive introduction for developers "
[6]: https://quickchat.ai/post/mcp-explained?utm_source=chatgpt.com "How Model Context Protocol works. MCP Explained - Quickchat AI"
[7]: https://www.nccgroup.com/us/research-blog/http-to-mcp-bridge/?utm_source=chatgpt.com "HTTP to MCP Bridge - NCC Group"
[8]: https://devblogs.microsoft.com/visualstudio/agent-mode-is-now-generally-available-with-mcp-support/?utm_source=chatgpt.com "Agent mode is now generally available with MCP support"
[9]: https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/overview?utm_source=chatgpt.com "What are tools in Azure AI Foundry Agent Service - Learn Microsoft"
[10]: https://www.reddit.com/r/GithubCopilot/comments/1kv3o66/how_to_tell_github_copilot_to_use_certain_mcp_tool/ "How to tell GitHub copilot to use certain MCP tool? : r/GithubCopilot"
[11]: https://devblogs.microsoft.com/semantic-kernel/integrating-model-context-protocol-tools-with-semantic-kernel-a-step-by-step-guide/?utm_source=chatgpt.com "Integrating Model Context Protocol Tools with Semantic Kernel"
[12]: https://techcommunity.microsoft.com/blog/azure-ai-services-blog/ai-automation-in-azure-foundry-through-turnkey-mcp-integration-and-computer-use-/4424098?utm_source=chatgpt.com "AI Automation in Azure Foundry through turnkey MCP Integration ..."
