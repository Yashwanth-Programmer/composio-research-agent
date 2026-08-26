# AI Product Ops — 100-App API & Agent Buildability Research

An AI-powered research agent built for the **Composio AI Product Ops take-home assignment**.

The agent researches software applications and evaluates their API and agent buildability using **Composio Search tools** and **Google Gemini**.

The final output is a structured JSONL dataset containing research findings and evidence URLs, followed by pattern analysis and an interactive HTML case study.

---

## Live Case Study

**Live Demo:**  
https://Yashwanth-Programmer.github.io/composio-research-agent/

**Source Repository:**  
https://github.com/Yashwanth-Programmer/composio-research-agent

---
**Instructions To Run**

1. Clone the repo
   git clone https://github.com/Yashwanth-Programmer/composio-research-agent.git
   cd composio-research-agent

2. Create a virtual environment
   Windows
   python -m venv venv
   venv\Scripts\activate
   
   macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt
   Our runner uses python-dotenv, the Composio SDK/Gemini provider, and the Google GenAI SDK.

4. Create .env
   Create .env in the same folder as run_batch.py:
   Put:
   COMPOSIO_API_KEY=your_composio_api_key
   GEMINI_API_KEY=your_gemini_api_key

5. The repository includes a completed `results.jsonl` dataset for inspection.

   The batch runner is resumable and skips apps already present in `results.jsonl`.  
## For a fresh run from all 100 apps, first empty: then run python python run_batch.py
   Note: Do not delete `results.jsonl`; remove it only when reproducing the research run from scratch.
   
   ```bash
   results.jsonl

# How Composio Was Used

Composio was used as the **tool layer for the research agent**.

Instead of implementing a custom web-search integration, the agent creates a Composio session with the `composio_search` toolkit and exposes those tools to Google Gemini.

Google Gemini acts as the reasoning and extraction layer, while Composio provides the external search capability used to gather evidence about each application.

### Research Flow

```text
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
   API / Documentation /
   MCP / Integration Evidence
            ↓
       Google Gemini
            ↓
    Structured JSON Result
            ↓
       results.jsonl
            ↓
      Pattern Analysis
            ↓
       patterns.json
            ↓
         index.html
What Composio Search Was Used For

For each application, the research agent uses the Composio search tools to investigate:

API availability
Authentication methods
Self-serve vs gated API access
API access requirements
REST / GraphQL availability
API breadth
MCP availability
Buildability
Integration blockers
Official documentation and evidence URLs
What Was Researched

100 applications across 10 categories were evaluated on:

What the application does
Authentication methods
Self-serve vs gated API access
Gate reason
API surface
API breadth
MCP availability
Buildability
Main blocker
Evidence URL
Confidence score
Project Structure
composio-research-agent/
│
├── index.html          # Final interactive HTML case study
├── results.jsonl       # Completed 100-app research dataset
├── patterns.json       # Aggregate research patterns
│
├── research_agent.py   # Research-agent implementation
├── run_batch.py        # Batch research runner
├── analyze.py          # Analysis utility
├── schema.py           # Research data schema
│
├── apps.csv            # Input list of applications
├── requirements.txt    # Python dependencies
├── .env                # Local environment variables (created locally)
├── .gitignore          # Prevents .env and local files from being committed
└── README.md           # Project documentation


