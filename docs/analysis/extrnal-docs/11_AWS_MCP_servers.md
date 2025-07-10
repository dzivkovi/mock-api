In short — AWS already maintains a **suite of >20 Model-Context-Protocol (MCP) servers**, but only a few are truly relevant to a *code-search / developer-knowledge* use-case.  The two you’ll want to study first are **Git Repo Research MCP Server** (semantic code search + file access) and **AWS Documentation MCP Server** (official docs search).  Both publish clear tool descriptions that show the LLM exactly *when* to call them, and their design patterns translate almost 1-for-1 to the “Teamcenter code-knowledge” server you’re planning.  Below are the concrete links, tool definitions, and “advertising blurbs” these servers expose, plus a checklist for re-using their patterns.

---

## 1  AWS MCP servers worth copying for code knowledge

| Server                                | What it does                                                                                                  | Why it matches your use-case                                                                                                   | Key tools (name → description)                                                                                                                                                                                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Git Repo Research MCP**             | Indexes any Git repo with FAISS + Bedrock embeddings and exposes semantic search, repo summaries, file access | Closest analogue to Teamcenter “master brain”. Handles hundreds-of-thousands-of-files scale.                                   | `create_research_repository` → “Index a Git repository for semantic search”; `search_research_repository` → “Query repository content using natural language and retrieve relevant code snippets”; `access_file` → “Read file or directory contents” ([awslabs.github.io][1]) |
| **AWS Documentation MCP**             | Searches AWS docs and converts pages to markdown                                                              | Shows how to wrap a *read-only* knowledge corpus with search + fetch; good pattern for internal coding standards docs          | `search_documentation` → “Search AWS documentation …”; `read_documentation` → “Fetch an AWS docs page and convert to markdown” ([awslabs.github.io][2])                                                                                                                       |
| **AWS OpenAPI MCP**                   | Dynamically turns any OpenAPI spec into MCP tools                                                             | Same FastMCP trick you’ll use: feed your existing Swagger file to auto-generate tools. (Link on site) ([awslabs.github.io][3]) |                                                                                                                                                                                                                                                                               |
| **Code Documentation Generation MCP** | Generates and indexes code docs for large repos                                                               | Optional inspiration if you later want AI-generated Teamcenter API docs ([awslabs.github.io][3])                               |                                                                                                                                                                                                                                                                               |

*(Other AWS servers—EKS, CDK, CloudWatch Logs, Prometheus, etc.—focus on infra or observability rather than source-code search, so they’re less relevant for now.)*

---

## 2  How these servers “advertise” themselves to LLMs

### 2.1 Naming & description pattern

* **Verb-led name** – e.g. `search_research_repository`
* **One-sentence description** that starts with *“Search…”, “Fetch…”, “Index…”*
* **Explicit domain keywords** (“repository”, “semantic search”, “documentation”) so the LLM’s string-matcher lights up
* **JSON-schema inputs** with intuitive field names (`query`, `filepath`, `limit`) ([awslabs.github.io][1], [awslabs.github.io][2])

### 2.2 Installation snippet (used by hosts)

Both servers publish a ready JSON block that an IDE pastes into its `mcp.json`; that block contains the command (`uvx …@latest`) plus env vars.  This doubles as human docs **and** an example prompt the LLM sees. ([awslabs.github.io][1], [awslabs.github.io][2])

### 2.3 “Use when …” guidance

The docs pages sprinkle natural-language examples:
*“Find README in aws-samples repo”* or *“Look up doc on S3 bucket naming”*.  These examples prime the foundation model to match similar user phrasing. ([awslabs.github.io][1], [awslabs.github.io][2])

---

## 3  Design checklist for your Teamcenter MCP server

1. **Start with the Git Repo Research template**

   * Fork the repo or mimic its FastMCP scaffolding (less than 300 LOC). ([awslabs.github.io][1])
2. **Feed your Swagger spec** to FastMCP’s `from_openapi()` to auto-create baseline tools. ([github.com][4])
3. **Rename & refine tools** so their names/descriptions echo developer language (“search\_teamcenter\_code”, “get\_file\_snippet”).
4. **Keep it read-only first** (`streaming_hint=True`, no write verbs) – aligns with AWS Documentation pattern.
5. **Publish a ready-to-paste `mcp.json` block** for teammates (copy AWS style).
6. **Add example prompts** in README (“Where is `BMIDE_import_export` implemented?”, “Show coding-standard for ‘Dataset’ class”).
7. **Smoke-test** with:

   ```bash
   curl -d '{"id":1,"method":"tools/list","params":{}}' http://localhost:8000/mcp
   ```

   Then stream a call (per pytest in DESIGN.md).
8. **Demo in two hosts tomorrow**

   * **Claude Desktop** ➜ add server URL, ask *“Search Teamcenter for ITK\_find\_object”*.
   * **VS Code Copilot** ➜ add same URL to `settings.json`, same prompt.

---

## 4  Learning links (Python & FastAPI focus)

| Topic                                                    | Link                                                                                                                                                                                                                                                     |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS “What’s New” announcement of MCP servers             | [https://aws.amazon.com/about-aws/whats-new/2025/05/new-model-context-protocol-servers-aws-serverless-containers](https://aws.amazon.com/about-aws/whats-new/2025/05/new-model-context-protocol-servers-aws-serverless-containers) ([aws.amazon.com][5]) |
| AWS Labs MCP GitHub org (all servers)                    | [https://github.com/awslabs/mcp](https://github.com/awslabs/mcp) ([github.com][6])                                                                                                                                                                       |
| Git Repo Research MCP docs                               | [https://awslabs.github.io/mcp/servers/git-repo-research-mcp-server/](https://awslabs.github.io/mcp/servers/git-repo-research-mcp-server/) ([awslabs.github.io][1])                                                                                      |
| AWS Documentation MCP docs                               | [https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/) ([awslabs.github.io][2])                                                                                      |
| Lambda Streamable-HTTP MCP demo                          | [https://github.com/mikegc-aws/Lambda-MCP-Server](https://github.com/mikegc-aws/Lambda-MCP-Server) ([github.com][7])                                                                                                                                     |
| AWS blog: “Unlocking the power of MCP on AWS”            | [https://aws.amazon.com/blogs/machine-learning/unlocking-the-power-of-model-context-protocol-mcp-on-aws/](https://aws.amazon.com/blogs/machine-learning/unlocking-the-power-of-model-context-protocol-mcp-on-aws/) ([aws.amazon.com][8])                 |
| AWS guidance for secure MCP deployment                   | [https://aws.amazon.com/solutions/guidance/deploying-model-context-protocol-servers-on-aws/](https://aws.amazon.com/solutions/guidance/deploying-model-context-protocol-servers-on-aws/) ([aws.amazon.com][9])                                           |
| How to build a serverless remote MCP (community post)    | [https://community.aws/content/2s44xHTSbQgo2Ws2bJr6hZsECGr/building-a-serverless-remote-mcp-server-on-aws-part-1](https://community.aws/content/2s44xHTSbQgo2Ws2bJr6hZsECGr/building-a-serverless-remote-mcp-server-on-aws-part-1) ([community.aws][10]) |
| FastMCP repo & docs                                      | [https://github.com/fastmcp/fastmcp](https://github.com/fastmcp/fastmcp) ([aws.amazon.com][5])                                                                                                                                                           |
| AWS “Introducing MCP servers for code assistants” series | [https://aws.amazon.com/blogs/machine-learning/introducing-aws-mcp-servers-for-code-assistants-part-1/](https://aws.amazon.com/blogs/machine-learning/introducing-aws-mcp-servers-for-code-assistants-part-1/) ([aws.amazon.com][11])                    |

*(Use only the Git Repo Research & AWS Docs servers for tomorrow’s demo; keep others for future expansion.)*

---

### Next step

Clone the Git Repo Research server tonight, replace its Bedrock/FAISS indexer with a stub that hits your `/stream` route, update tool names/descriptions per §3 above, and you’ll have a working proof-of-concept MCP server ready for the meeting.

[1]: https://awslabs.github.io/mcp/servers/git-repo-research-mcp-server/ "Git Repo Research MCP Server - AWS MCP Servers"
[2]: https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/ "AWS Documentation MCP Server - AWS MCP Servers"
[3]: https://awslabs.github.io/mcp/ "AWS MCP Servers"
[4]: https://github.com/aws-samples/aws-mcp-servers-samples?utm_source=chatgpt.com "aws-samples/aws-mcp-servers-samples - GitHub"
[5]: https://aws.amazon.com/about-aws/whats-new/2025/05/new-model-context-protocol-servers-aws-serverless-containers?utm_source=chatgpt.com "Announcing new Model Context Protocol (MCP) Servers for AWS ..."
[6]: https://github.com/awslabs/mcp?utm_source=chatgpt.com "awslabs/mcp: AWS MCP Servers — helping you get the ... - GitHub"
[7]: https://github.com/mikegc-aws/Lambda-MCP-Server?utm_source=chatgpt.com "Lambda MCP Server Demo (Streamable HTTP) - GitHub"
[8]: https://aws.amazon.com/blogs/machine-learning/unlocking-the-power-of-model-context-protocol-mcp-on-aws/?utm_source=chatgpt.com "Unlocking the power of Model Context Protocol (MCP) on AWS"
[9]: https://aws.amazon.com/solutions/guidance/deploying-model-context-protocol-servers-on-aws/?utm_source=chatgpt.com "Guidance for Deploying Model Context Protocol Servers on AWS"
[10]: https://community.aws/content/2s44xHTSbQgo2Ws2bJr6hZsECGr/building-a-serverless-remote-mcp-server-on-aws-part-1?utm_source=chatgpt.com "Building a Serverless remote MCP Server on AWS - Part 1"
[11]: https://aws.amazon.com/blogs/machine-learning/introducing-aws-mcp-servers-for-code-assistants-part-1/?utm_source=chatgpt.com "Introducing AWS MCP Servers for code assistants (Part 1)"
