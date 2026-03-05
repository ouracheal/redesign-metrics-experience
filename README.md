# Bits — AI Metrics Explorer

A reimagined Datadog Metrics Explorer with **Bits**, an AI assistant that lets engineers explore metrics conversationally and take action in real time.

Built for the Datadog hackathon.

---

## What it does

- **Natural language search** — type what you're looking for ("checkout failures by region") and land on the right view automatically
- **Bits AI sidebar** — chat with Bits to change aggregations, break down by tag, compare time periods, and get explanations without touching the query builder
- **Live Datadog data** — Bits uses the Datadog MCP server to query real metrics, monitors, dashboards, and logs
- **Dual timeseries comparison** — say "compare to last week" and instantly see two separate charts side by side with query rows a and b
- **Smart routing** — list queries go to the metrics search page, graph queries go to the explorer

## Pages

| File | Description |
|---|---|
| `metrics-explorer.html` | Main entry point with AI search |
| `query-result.html` | Metric explorer with Bits chat sidebar and query builder |
| `search-results.html` | Browsable metrics list |
| `health-monitoring.html` | Health monitoring dashboard |
| `cost-optimization.html` | Cost optimization view |
| `platform-health-dashboard.html` | Platform health overview |

## Stack

- **Frontend** — pure HTML/CSS/JS, no bundler
- **Backend** — Python (FastAPI) + Anthropic Claude API + Datadog MCP
- **AI** — Claude Sonnet with an agentic tool loop; local intents handle graph mutations instantly, everything else hits the server

## Setup

```bash
cp .env.example .env
# Fill in DD_API_KEY, DD_APP_KEY, ANTHROPIC_API_KEY

pip install fastapi uvicorn anthropic httpx python-dotenv
python3 server.py
```

Then open any `.html` file in your browser. The Bits sidebar connects to `http://localhost:7788`.

## Environment variables

| Variable | Description |
|---|---|
| `DD_API_KEY` | Datadog API key |
| `DD_APP_KEY` | Datadog application key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `DD_SITE` | Datadog site (default: `datadoghq.com`) |
