# Basic MCP Server — a learning build

A minimal [Model Context Protocol](https://modelcontextprotocol.io/) server,
built from scratch to understand how MCP tools work and how an AI client
selects and calls them.

Built with **FastMCP** (from the official `mcp` Python SDK). Connected to and
tested with both the **MCP Inspector** and **Cursor** as the AI client.

> **Note:** Some tools in this server are *intentionally* buggy. This is a
> learning repo — the bugs are deliberate experiments, kept in on purpose to
> demonstrate how MCP tool selection behaves (and misbehaves). See "What this
> demonstrates" below. Do not treat this as a correct calculator.

## What MCP is (the one-line version)

An MCP server is like a web API, but designed for LLMs: it exposes **tools**
(like POST endpoints — they run code) that an AI client can discover and call.
You write a normal Python function, add an `@mcp.tool()` decorator, and FastMCP
auto-generates the tool's schema (name, arguments, description) from your type
hints and docstring. The AI reads that schema and decides — on its own — which
tool to call from a plain-English request.

## The tools in this server

| Tool       | Description (what the AI sees) | Code (what actually runs) | Honest? |
|------------|-------------------------------|---------------------------|---------|
| `add`      | "Add two numbers"             | `a + b`                   | yes  |
| `subtract` | "Subtract two numbers"        | `a * b`                   | **NO — lies, returns the product** |
| `minus`    | "difference of two numbers"   | `a - b`                   | yes (the real subtraction) |
| `multiply` | "multiply of two numbers"     | `a * b`                   | yes  |

## What this demonstrates

Tested by connecting the server to Cursor and asking plain-English questions:

1. **Automatic tool calls** — "What is 8 plus 5?" → the AI called `add` on its
   own and answered 13. No manual tool selection.
2. **Selection under ambiguity** — `subtract` and `minus` both relate to
   "minus." Asked "What is 6 minus 2?", the AI chose `minus` (the honest tool)
   and correctly answered 4.
3. **Fallback to its own knowledge** — there is no division tool, so "What is 6
   divided by 2?" was answered (3) by the model directly, *without* a tool. Tools
   are optional, not mandatory.
4. **A lying tool = a confident wrong answer** — forced to use `subtract`
   ("Use the subtract tool to compute 6 and 2"), the AI returned **12** (the
   product) with full confidence, because it trusts the tool's description, not
   its code. The model has no way to know the code contradicts the name.

### The key takeaway

A tool's **docstring and name are load-bearing** — the AI reasons over them to
decide what to call. If the description and the code disagree, you get a
confident wrong answer, and *most MCP clients cannot detect it* (they only see
the interface and the result, never the source). Cursor happened to catch the
`subtract` bug here only because it can also read the source files — a pure MCP
client would not have. This is why real-world MCP practice is: keep tool sets
small and descriptions sharp and accurate.

## Setup

Requires Python 3.10+.

```bash
pip install "mcp[cli]"
```

## Run / test

**With the MCP Inspector** (a browser UI to call tools by hand):

```bash
mcp dev server.py
```

**With Cursor** (the AI client): add this to `.cursor/mcp.json`, pointing
`command` at your Python executable:

```json
{
  "mcpServers": {
    "demo-math": {
      "command": "C:\\path\\to\\python.exe",
      "args": ["C:\\path\\to\\server.py"]
    }
  }
}
```

Then enable it under Cursor → Settings → Tools & MCPs, and chat with the Agent.

## Things I learned building this

- A tool is just a Python function plus an `@mcp.tool()` **decorator**; FastMCP
  generates the schema from type hints + docstring.
- The AI **reasons** over tool descriptions to pick one — this is *not* the
  cosine-similarity math used in RAG retrieval. It's the model's own tool-use
  ability.
- `ENOENT` errors mean "a command this needs isn't installed / not on PATH"
  (hit it with both `uv` and the Inspector's Node dependency).
- For stdio servers, **the client launches the server** — you don't run it
  yourself; you give the client the launch command.

## Next step

Wrap a real capability as a tool — e.g. expose a RAG pipeline's `answer()`
function as an MCP tool, so an AI client can query a document set through this
same mechanism.
