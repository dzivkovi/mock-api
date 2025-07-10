# MCP Tool Advertising: The Art of Being Discovered

> **Core Principle:** LLMs choose MCP tools based on keyword matching between user queries and tool descriptions. Perfect advertising = perfect keyword alignment.

## The Formula for Perfect Tool Discovery

### 1. Tool Name = Action + Domain
```
✅ teamcenter_search    (search + teamcenter)
✅ search_documentation (search + documentation) 
✅ ask_question        (ask + question)

❌ processQuery        (generic, no domain)
❌ handleRequest       (unclear action)
```

### 2. Description = Verb + Object + Domain Keywords
```
✅ "Search the Teamcenter knowledge base for technical information and documentation"
   ↳ Contains: search, Teamcenter, knowledge base, technical, documentation

✅ "Ask any question about a GitHub repository"
   ↳ Contains: ask, question, GitHub, repository

❌ "Process user input and return results"
   ↳ Generic, no domain keywords
```

### 3. Parameter Names = Natural Language
```
✅ search_query, sessionID, topNDocuments
✅ repoName, question, limit

❌ input, params, config
```

## Real-World Invocation Triggers

**User says:** "Find where the BMIDE_import_export function is implemented"
**LLM thinks:** *search + code + function* → calls `teamcenter_search`

**User says:** "What does the Dataset class do in our Teamcenter setup?"
**LLM thinks:** *question + Teamcenter + class* → calls `teamcenter_search`

**User says:** "Show me documentation about S3 bucket naming"
**LLM thinks:** *documentation + show* → calls `search_documentation`

## Our Two Servers: Invocation Analysis

### Basic MCP (`basic_mcp.py`)
```python
@mcp.tool()
async def teamcenter_search(search_query: str, sessionID: str, topNDocuments: int = 5) -> str:
    """Search the Teamcenter knowledge base for technical information and documentation."""
```

**Trigger words:** search, Teamcenter, knowledge, technical, documentation
**User queries that work:**
- "Search Teamcenter for PLM functions"
- "Find Teamcenter documentation about datasets"
- "What technical information exists about BMIDE?"

### Auto-Generated MCP (`auth_openapi_mcp.py`)
```python
# Auto-generates 5 tools from OpenAPI spec
# Names: get_health, get_home, get_stream, post_add_rating, get_root
```

**Problem:** Generic tool names like `get_stream` lack domain keywords
**Solution:** LLM sees multiple tools, picks based on parameter patterns

## AWS Gold Standard Examples

**Git Repo Research MCP:**
- `search_research_repository` → "Query repository content using natural language"
- Perfect keywords: search, repository, content, natural language

**AWS Documentation MCP:**
- `search_documentation` → "Search AWS documentation"
- Perfect keywords: search, AWS, documentation

## The Three Laws of MCP Advertising

### Law 1: Mirror User Language
Write descriptions using words developers actually say:
- "Search" not "Query"
- "Find" not "Locate" 
- "Documentation" not "Docs"
- "Knowledge base" not "Information system"

### Law 2: Front-Load Keywords
Put the most important keywords first:
```
✅ "Search the Teamcenter knowledge base..."
❌ "Access enterprise PLM systems to search..."
```

### Law 3: One Tool, One Purpose
Don't create Swiss Army knife tools:
```
✅ teamcenter_search    (focused: search only)
✅ teamcenter_get_file  (focused: file retrieval)

❌ teamcenter_handler   (unclear: does everything)
```

## Implementation Checklist

### ✅ Our Current Implementation
- [x] Clear tool name: `teamcenter_search`
- [x] Domain keywords in description: "Teamcenter knowledge base"
- [x] Action verb: "Search"
- [x] Natural parameter names: `search_query`, `sessionID`
- [x] Focused purpose: search only

### 🎯 Optimization Opportunities
- [ ] Add example queries to documentation
- [ ] Consider additional focused tools: `teamcenter_get_file`, `teamcenter_browse_docs`
- [ ] Test with different user query patterns
- [ ] Add metadata hints for common use cases

## Testing Tool Discovery

**Method:** Ask these questions and see which tool gets called:

1. "Search for PLM functions in Teamcenter"
2. "Find documentation about datasets"  
3. "What technical information exists about BMIDE?"
4. "Look up Teamcenter API documentation"
5. "Browse knowledge base for import/export functions"

**Expected:** All should trigger `teamcenter_search`

## The Perfect Tool Description Template

```python
@mcp.tool()
async def {domain}_{action}({natural_params}) -> str:
    """{Action} the {Domain} {object} for {use_case} and {secondary_use_case}."""
```

**Example:**
```python
@mcp.tool()
async def teamcenter_search(search_query: str, sessionID: str, topNDocuments: int = 5) -> str:
    """Search the Teamcenter knowledge base for technical information and documentation."""
```

## Success Metrics

**Perfect advertising achieved when:**
- LLM chooses correct tool 95%+ of the time
- Users don't need to specify tool names explicitly  
- Tool gets invoked for both direct commands ("search X") and questions ("what is Y?")
- Zero false positives (wrong tool selected)

## Future Enhancement: Context Hints

**Advanced pattern from AWS:**
```python
# Add context hints for better discovery
@mcp.tool(
    tags=["search", "knowledge", "teamcenter", "plm"],
    examples=["Find PLM functions", "Search Teamcenter docs"]
)
```

---

**Bottom Line:** Perfect MCP advertising is about speaking the user's language before they even ask the question. Every word in your tool name and description is a vote for when your tool should be called.