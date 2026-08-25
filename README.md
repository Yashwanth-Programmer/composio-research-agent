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
composio-research-agent/
├── .env
├── run_batch.py
├── apps.csv
└── ...
Put:
COMPOSIO_API_KEY=your_composio_api_key
GEMINI_API_KEY=your_gemini_api_key

5. Run the research agent
python run_batch.py 

7. View the existing completed results clear and run it
The repository already contains the completed research output:
results.jsonl

run python analyze.py for patterns in json format

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

Note: .env is shown in the structure for clarity. It is intentionally not included in the GitHub repository or submission ZIP because it contains API credentials. It must be created locally during setup.

Setup & Usage
1. Clone the Repository
git clone https://github.com/Yashwanth-Programmer/composio-research-agent.git
cd composio-research-agent
2. Create a Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies

Install all required Python packages:

pip install -r requirements.txt
4. Configure Environment Variables

The research agent requires API credentials for Composio and Google Gemini.

Create a file named:

.env

in the root directory of the project, at the same level as run_batch.py.

The project should look like:

composio-research-agent/
│
├── .env
├── run_batch.py
├── research_agent.py
├── apps.csv
└── ...
Add the following variables to .env
COMPOSIO_API_KEY=your_composio_api_key
GEMINI_API_KEY=your_gemini_api_key

Replace the placeholder values with your actual API credentials.

Example
COMPOSIO_API_KEY=xxxxxxxxxxxxxxxx
GEMINI_API_KEY=xxxxxxxxxxxxxxxx

The example values above are placeholders and are not actual credentials.

Where the keys are used
COMPOSIO_API_KEY — authenticates the application with Composio and enables access to the configured Composio tools.
GEMINI_API_KEY — authenticates requests to Google Gemini used by the research agent.
Important Security Note

The .env file contains sensitive API credentials.

For security reasons:

Do not commit .env to GitHub.
Do not upload .env to the submission repository.
Do not share API keys in source code.
The .gitignore file excludes .env from Git tracking.

The .env file shown in the project structure represents a local file created by the person running the project.

Running the Research Agent

Once the virtual environment is activated, dependencies are installed, and .env is configured, run:

python run_batch.py

The batch runner:

Reads the applications from apps.csv.
Determines which applications need to be researched.
Creates a Composio session with the composio_search toolkit.
Provides the Composio tools to Google Gemini.
Researches API, authentication, MCP, and integration information.
Extracts the findings into the required structured JSON format.
Retries failed research requests.
Writes completed results incrementally to results.jsonl.
Research Output

The completed research dataset is stored in:

results.jsonl

Each line represents one application's research result.

A typical record looks like:

{
  "one_liner": "Example application description.",
  "auth_methods": [
    "API key"
  ],
  "self_serve": "self-serve",
  "gate_reason": "none",
  "api_surface": "REST",
  "api_breadth": "broad",
  "mcp_exists": true,
  "buildability": "yes",
  "blocker": "",
  "evidence_url": "https://example.com/docs",
  "confidence": 1.0,
  "_app_name": "Example"
}

The final research dataset contains:

100 applications
100 research records
10 categories
Authentication information
API access information
MCP availability
Buildability assessments
Evidence URLs
Confidence scores
Pattern Analysis

The aggregate analysis is available in:

patterns.json

It contains patterns derived from the completed research dataset, including:

Authentication distribution
Self-serve vs gated access
API surface
API breadth
MCP availability
Buildability
Category-level patterns
Integration blockers
Interactive Case Study

The final interactive case study is:

index.html

It presents:

Executive findings
Authentication patterns
API access patterns
Self-serve vs gated access
Buildability analysis
MCP availability
Category-level patterns
Integration blockers
Complete 100-app research matrix
Evidence links
Search and filtering functionality

The case study is deployed using GitHub Pages.

Live Case Study:

https://Yashwanth-Programmer.github.io/composio-research-agent/

Error Handling

The research workflow includes basic handling for unpredictable tool and model behavior.

JSON Parsing

The research agent attempts to parse the model's structured JSON response and includes fallback handling for malformed responses.

Retries

Failed research requests are retried multiple times.

Timeouts

Individual research calls have a timeout so that a single application does not block the entire batch indefinitely.

Rate Limits

The runner handles retry delays when requests are rate-limited.

Incremental Output

Results are written to results.jsonl immediately after each application is processed.

This preserves completed research if the batch process is interrupted.

Reproducibility

The complete research workflow can be rerun from the supplied application list.

Input
apps.csv
Run
python run_batch.py
Output
results.jsonl

The analysis and final case study are based on the resulting structured research data.

Final Deliverables

The repository contains:

index.html          → Interactive HTML case study
results.jsonl       → 100-app research dataset
patterns.json       → Aggregate research analysis
research_agent.py   → Research-agent implementation
run_batch.py        → Batch execution workflow
schema.py           → Research data schema
analyze.py          → Analysis utility
apps.csv            → Input application list
requirements.txt    → Python dependencies
README.md           → Setup and project documentation
Note

This research covers the 100 applications selected for the assignment. The findings represent observations from this research set and are not intended to represent the entire software market.


**This is the version I'd submit.** The reviewer gets an unambiguous path:

`clone → venv → pip install → create .env → add two keys → run → inspect results → open case study`

while your actual API credentials remain private.
all this should be in readme.md 

Yes. All of the content above should be inside your README.md file.

You should not create separate files for the setup instructions, .env instructions, Composio explanation, etc.

Your GitHub repo should have:

composio-research-agent/
│
├── README.md          ← ALL documentation goes here
├── index.html
├── requirements.txt
├── research_agent.py
├── run_batch.py
├── analyze.py
├── schema.py
├── apps.csv
├── results.jsonl
├── patterns.json
└── .gitignore

The .env is mentioned in the README, but not uploaded:

.env  ← create locally after cloning

So when the reviewer opens README.md, they can read everything in one place:

What the project is
How Composio was used
Research flow
What was researched
Project structure
How to clone
How to create venv
How to install requirements.txt
Exactly how to create .env
Which environment variables are required
How to run python run_batch.py
Where results are saved
How pattern analysis works
How to open the case study
Error handling
Reproducibility
Final deliverables

So yes: take the final README I gave you and paste the entire thing into README.md.

give me final.md file 

Done. I created the final README.md with the complete setup, .env instructions, Composio usage, Gemini workflow, execution steps, outputs, error handling, reproducibility, and case-study information.

Download the final README.md 

README.md
Document
