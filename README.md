# AI Product Ops — 100-App API & Agent Buildability Research

An AI-powered research agent built for the Composio AI Product Ops take-home assignment.

The agent researches software applications and evaluates their API and agent buildability using **Composio Search tools** and **Google Gemini**. The final output is a structured JSONL dataset containing research findings and evidence URLs, followed by pattern analysis and an interactive HTML case study.
## How Composio Was Used

Composio was used as the **tool layer for the research agent**.

Instead of giving the LLM direct access to a custom web-search implementation, the agent creates a Composio session with the `composio_search` toolkit and exposes those tools to Google Gemini.

### Research Flow

Application Name + Hint URL
            ↓
       Google Gemini
       (Research Agent)
            ↓
     Composio Tool Layer
            ↓
      composio_search
            ↓
        Web Search
            ↓
   Relevant documentation
   / API / MCP evidence
            ↓
       Google Gemini
            ↓
    Structured JSON result


## What Was Researched

100 applications across 10 categories were evaluated on:

- What the application does
- Authentication methods
- Self-serve vs gated API access
- Gate reason
- API surface
- API breadth
- MCP availability
- Buildability
- Main blocker
- Evidence URL
- Confidence

## Project Structure

```text
composio-research-agent/
│
├── index.html          # Final interactive HTML case study
├── results.jsonl       # Completed 100-app research dataset
├── patterns.json       # Aggregate research patterns
│
├── research_agent.py   # Research-agent implementation
├── run_batch.py        # Batch research runner
├── analyze.py          # Analysis script
├── schema.py           # Research data schema
│
├── apps.csv            # Input list of applications
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation