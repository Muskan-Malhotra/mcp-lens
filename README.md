# MCP Lens 🔎

> Observe what your MCP agent did — not just whether the tool call succeeded.

MCP Lens is a lightweight observability and behavior-analysis layer for MCP tool interactions.

It was built to answer a question that most agent logs still miss:

**If an AI agent makes the wrong decision while using an MCP tool, will the logs actually tell me what went wrong?**

A normal MCP interaction may look healthy:

```text
search_customer → success
get_customer_history → success
```

Both calls succeeded.

But what if the first search returned two customers with the same name, and the agent simply picked one?

The requests succeeded.  
The decision did not.

MCP Lens is an experiment in making that kind of behavior visible.

---

## Why This Matters

Most observability tools focus on protocol-level success:

- tool was called
- request returned
- server responded
- status was 200

That tells us what happened technically.

It does not always tell us whether the agent made a safe or correct decision.

With multi-step tool workflows, the dangerous part is often not the failed request. It is the ambiguous follow-up decision made after a successful result.

MCP Lens is designed for exactly that gap.

---

## The Problem

MCP makes it easy for an agent to discover and call tools, but debugging multi-tool decision-making is still hard.

Example:

```text
User: "Get Alice's customer history."

Agent
  ↓
search_customer("Alice")
  ↓
C001 - Alice
C004 - Alice
  ↓
get_customer_history("C001")
```

There are two customers named Alice.

The agent selected `C001` without asking the user which Alice they meant.

Nothing necessarily failed at the protocol level.

- The MCP server worked.
- The tools worked.
- The requests returned successfully.

But the sequence of decisions was questionable.

That is the kind of problem MCP Lens is meant to surface.

---

## What MCP Lens Does

MCP Lens currently does three things:

1. Traces MCP tool calls
2. Inspects tool results
3. Detects decision patterns across consecutive tool calls

Example flow:

```text
search_customer("Alice")
        ↓
2 matching customers
        ↓
AMBIGUOUS_RESULT
        ↓
get_customer_history("C001")
        ↓
AMBIGUOUS_SELECTION
```

Instead of only showing:

```text
200 OK
```

MCP Lens can reveal:

```text
The search returned 2 customers,
but the next tool call selected C001
without clarification.
```

---

## The “Two Alices” Example

This is the main scenario being used in the prototype.

The example server contains two customers with the name `Alice`:

```text
C001 - Alice
C004 - Alice
```

When the agent searches:

```python
search_customer("Alice")
```

the tool returns:

```json
[
  {
    "id": "C001",
    "name": "Alice"
  },
  {
    "id": "C004",
    "name": "Alice"
  }
]
```

It intentionally does not return email, history, or risk at this stage.

The idea is simple: if the result is ambiguous, we do not need more information just to determine that the result itself is ambiguous.

MCP Lens detects this as:

```text
AMBIGUOUS_RESULT
severity: warning
```

If the agent then does:

```python
get_customer_history("C001")
```

without clarification, Lens detects a second issue:

```text
AMBIGUOUS_SELECTION
severity: high
```

This distinction matters.

### AMBIGUOUS_RESULT

The tool returned multiple possible entities.

### AMBIGUOUS_SELECTION

The agent acted on one of those entities without resolving the ambiguity.

---

## Why This Is Different From Basic Logging

A basic log might show:

```text
search_customer
status: success

get_customer_history
status: success
```

MCP Lens keeps the individual traces, but also asks:

> What happened between these calls?

This allows us to move from:

```text
"What did the MCP server do?"
```

towards:

```text
"What did the agent do with what the MCP server gave it?"
```

That is the heart of the project.

---

## Who This Helps

This project is valuable for:

- AI agent developers
- teams debugging multi-tool workflows
- MCP integrators
- observability engineers
- safety and evaluation teams
- anyone building agent systems where tool selection affects downstream behavior

### What they do today

Most teams still rely on:

- raw tool success/failure logs
- request/response traces
- ad hoc debugging with manual replay

These are not enough when the failure is behavioral rather than protocol-level.

### How this helps

It reduces the time required to answer:

- Why did the agent choose this entity?
- Did the tool output create ambiguity?
- Did the agent act unsafely after an ambiguous result?

That is meaningful practical value.

---

## Failure Modes It Detects

The current prototype already captures several relevant patterns:

- ambiguous search results
- unsafe follow-up selection after ambiguity
- decision flows that look successful but are semantically risky
- multi-step tool behavior that is not obvious from raw logs

This gives the project a strong foundation for future safety and observability features.

---

## Architecture

The current prototype is intentionally small:

```text
                AI Agent
                    │
                    ▼
                MCP Client
                    │
                    ▼
              ┌─────────────┐
              │  MCP Lens   │
              │             │
              │   Tracer    │
              │      ↓      │
              │   Analyzer  │
              └──────┬──────┘
                     │
                     ▼
                 MCP Server
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Search     History      Risk
```

### Tracer

The tracer records information about a tool execution:

- Trace ID
- Tool name
- Arguments
- Status
- Result
- Execution time

### Analyzer

The analyzer currently looks for:

- Ambiguous customer search results
- An agent selecting a customer after an ambiguous search

The analyzer is intentionally rule-based right now so the behavior is easy to understand and reproduce.

---

## Project Structure

```text
mcp-lens/
│
├── src/
│   └── mcp_lens/
│       ├── __init__.py
│       ├── analyzer.py
│       └── tracer.py
│
├── sample/
│   └── server.py
│
├── tests/
│   └── test_analyzer.py
│
├── client.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

The `sample/` directory contains the MCP server used for the demo.

The `src/mcp_lens/` directory contains the actual Lens implementation.

---

## Getting Started

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- MCP Python SDK 2.x

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/mcp-lens.git
cd mcp-lens
```

### Install dependencies

```bash
uv sync
```

---

## Run the Demo

The easiest way to see MCP Lens in action is to run the client:

```bash
uv run python3 client.py
```

The client connects to the example MCP server, discovers its tools, and executes the demo interaction.

You should see output similar to:

```text
- search_customer:
  Search customer by name

- get_customer_history:
  Get customer history by ID

- calculate_risk:
  Calculate churn risk for a specific customer


[LENS] - search_customer

Trace:
{
  "tool": "search_customer",
  "arguments": {
    "name": "Alice"
  },
  "status": "success",
  "result": {
    "result": [
      {
        "id": "C001",
        "name": "Alice"
      },
      {
        "id": "C004",
        "name": "Alice"
      }
    ]
  }
}

MCP LENS FINDING

Type: AMBIGUOUS_RESULT
Severity: warning

Message:
Search returned 2 customers with the same name.

Recommendation:
Ask the user to clarify which customer they mean
before accessing customer data.


[LENS] - get_customer_history

History Trace:
{
  "tool": "get_customer_history",
  "arguments": {
    "customer_id": "C001"
  },
  "status": "success"
}

MCP LENS FINDING

Type: AMBIGUOUS_SELECTION
Severity: high

Message:
The search returned 2 customers, but the next tool call
selected C001 without clarification.

Recommendation:
Require disambiguation before accessing
customer-specific information.
```

The second finding is intentionally triggered by the demo so the behavior is easy to see and reason about.

---

## Run the Tests

Run:

```bash
uv run pytest
```

The current tests cover both normal and problematic behavior:

- A unique customer should not trigger an ambiguity warning
- Duplicate customers should trigger `AMBIGUOUS_RESULT`
- Selecting one customer after an ambiguous search should trigger `AMBIGUOUS_SELECTION`
- A valid unique-customer follow-up should not trigger an unsafe-selection warning
---

## Current Status

This is an early prototype.

### Implemented

- [x] MCP server using MCP Python SDK 2.x
- [x] MCP client
- [x] MCP tool discovery
- [x] Tool invocation
- [x] Tool tracing
- [x] Trace IDs
- [x] Tool arguments and results
- [x] Ambiguous-result detection
- [x] Cross-tool behavioral analysis
- [x] Ambiguous-selection detection
- [x] Basic analyzer tests

---

## Roadmap

The current implementation is intentionally small.

The longer-term idea is to make MCP Lens function as a layer between an agent and MCP servers:

```text
                 AI Agent
                     │
                     ▼
              ┌─────────────┐
              │  MCP Lens   │
              │    Proxy    │
              ├─────────────┤
              │   Trace     │
              │   Analyze   │
              │   Detect    │
              │   Replay    │
              └──────┬──────┘
                     │
                     ▼
                 MCP Server
```

### Behavioral patterns to explore

```text
RETRY_LOOP
UNEXPECTED_TOOL
TOOL_SEQUENCE_ANOMALY
EXCESSIVE_TOOL_CALLS
AMBIGUOUS_SELECTION
```

### Potential data and safety signals

- requests more information than necessary
- accesses entity-specific data without sufficient context
- continues after an ambiguous tool result

### Debugging vision

Eventually, a developer could inspect an entire agent execution:

```text
Trace
 │
 ├── search_customer
 │
 ├── AMBIGUOUS_RESULT
 │
 ├── get_customer_history
 │
 └── AMBIGUOUS_SELECTION
```

and understand why a seemingly successful run deserves investigation.

---

## Why I Built This

I’ve been working with MCP and agent-based systems, and one thing that keeps bothering me is that the interesting failures are not always traditional failures.

A tool can return successfully.

The next tool can return successfully.

And the agent can still do the wrong thing.

The “two Alices” example is intentionally simple, but it captures that problem well.

It made me think about observability differently:

> Maybe observing an agent is not only about recording what happened. It is also about understanding the decisions between tool calls.

MCP Lens is my attempt to explore that idea.

---

## Status

Early prototype / work in progress

Built as an exploration of MCP observability and agent behavior analysis.

---

## License

MIT
