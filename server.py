"""
Bits Assistant backend — Claude + Datadog MCP HTTP server.
Exposes POST /api/chat for the metrics-explorer HTML front-end.

Setup:
  cp .env.example .env   # fill in your keys
  python3 server.py
"""

import os, json, re, asyncio, httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import anthropic
from dotenv import load_dotenv

load_dotenv()

DD_API_KEY        = os.getenv("DD_API_KEY", "")
DD_APP_KEY        = os.getenv("DD_APP_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DD_MCP_URL        = os.getenv("DD_MCP_URL", "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp")
DD_SITE           = os.getenv("DD_SITE", "datadoghq.com")
DD_BASE_URL       = f"https://app.{DD_SITE}"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Datadog MCP helpers ────────────────────────────────────────────────────

DD_HEADERS = {
    "DD-API-KEY":          DD_API_KEY,
    "DD-APPLICATION-KEY":  DD_APP_KEY,
    "Content-Type":        "application/json",
}

async def mcp_call(method: str, params: dict | None = None) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params:
        payload["params"] = params
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(DD_MCP_URL, headers=DD_HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"MCP error: {data['error']}")
        return data.get("result", {})


async def get_mcp_tools() -> list[dict]:
    try:
        result = await mcp_call("tools/list")
        return [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": t.get("inputSchema", {"type": "object", "properties": {}}),
            }
            for t in result.get("tools", [])
        ]
    except Exception as e:
        print(f"Warning: could not fetch MCP tools: {e}")
        return []


async def call_mcp_tool(name: str, args: dict) -> str:
    try:
        result = await mcp_call("tools/call", {"name": name, "arguments": args})
        parts = []
        for c in result.get("content", []):
            if isinstance(c, dict):
                if c.get("type") == "text":
                    parts.append(c.get("text", ""))
                elif c.get("type") == "resource":
                    parts.append(json.dumps(c.get("resource", {}), indent=2))
            else:
                parts.append(str(c))
        return "\n".join(parts) or json.dumps(result)
    except Exception as e:
        return f"Tool error: {e}"


# ── Action parsing ─────────────────────────────────────────────────────────

def parse_actions(text: str) -> tuple[str, list[dict]]:
    """
    Strip ACTION:{...} directives from Claude's reply.
    Returns (clean_text, list_of_action_dicts).
    """
    actions = []
    clean_lines = []
    for line in text.split("\n"):
        m = re.match(r"^ACTION:(\{.+\})\s*$", line.strip())
        if m:
            try:
                actions.append(json.loads(m.group(1)))
            except Exception:
                pass
        else:
            clean_lines.append(line)
    return "\n".join(clean_lines).rstrip(), actions


# ── System prompt ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are **Bits**, an intelligent AI assistant embedded in Datadog's Metrics Explorer sidebar.
You are talking with an engineer who is actively looking at a metric on screen.

PERSONALITY
- Friendly, concise, data-driven — like a knowledgeable SRE colleague
- Ask follow-up questions to understand what the engineer actually needs
- Never say "I cannot" without explaining *why* and offering an alternative
- When you do something to the graph, say what changed and what to look for

CAPABILITIES
1. **Graph control** — you can change the graph in real-time using ACTION directives (see below)
2. **Live Datadog data** — you have real Datadog tools: query metrics, list monitors, list dashboards, search logs
3. **Monitor creation** — guide the engineer step-by-step, then create via tool or give a pre-filled Datadog link
4. **Documentation** — always cite docs when explaining limits or pointing elsewhere

GRAPH ACTION DIRECTIVES
When you want to change the graph, include ONE OR MORE of these on their own lines at the END of your reply.
The UI will execute them and show the change to the engineer.

  ACTION:{{"type":"set_agg","value":"p99"}}
  ACTION:{{"type":"set_group","value":"host"}}
  ACTION:{{"type":"add_comparison","label":"last week"}}
  ACTION:{{"type":"remove_comparison"}}
  ACTION:{{"type":"open_url","url":"URL_HERE","label":"Button label"}}

MONITOR CREATION FLOW
When asked to create a monitor:
1. Confirm the metric, filter, and what condition should trigger
2. If threshold not given, suggest a sensible default based on the current data range
3. Ask for notification channel (@slack-channel, @pagerduty, email) — or proceed without if engineer says to skip
4. Try to create it via the create_monitor MCP tool if available
5. Always end with an ACTION open_url pointing to the Datadog monitor create page with the query pre-filled:
   {DD_BASE_URL}/monitors/create?query=<url-encoded-query>
6. Summarise exactly what was configured

WHEN YOU CANNOT DO SOMETHING
- Explain *why* clearly and briefly (e.g. "I don't have write access to X")
- Give the exact Datadog UI path or a direct docs link: https://docs.datadoghq.com
- Offer the closest thing you *can* do

FORMAT
- Keep replies short — you are in a narrow sidebar
- Use **bold** for metric names, numbers, and key terms
- Use line breaks for lists — avoid bullet overload
- Never repeat the user's question back to them

Current page context is injected with each message.
"""


# ── Claude agentic loop ────────────────────────────────────────────────────

async def run_claude(messages: list[dict], context: dict) -> dict:
    """
    Run Claude with Datadog MCP tools. Returns {"reply": str, "actions": list}.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    tools  = await get_mcp_tools()

    ctx_str = json.dumps(context, indent=2) if context else "{}"
    system  = SYSTEM_PROMPT + f"\n\n---\nCURRENT PAGE CONTEXT:\n{ctx_str}\n---"

    claude_messages = list(messages)

    for _ in range(10):
        kwargs = dict(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system,
            messages=claude_messages,
        )
        if tools:
            kwargs["tools"] = tools

        response = client.messages.create(**kwargs)

        if response.stop_reason == "end_turn":
            raw_text = " ".join(
                b.text for b in response.content if hasattr(b, "text")
            )
            reply, actions = parse_actions(raw_text)
            return {"reply": reply, "actions": actions}

        if response.stop_reason == "tool_use":
            tool_blocks = [b for b in response.content if b.type == "tool_use"]
            claude_messages.append({"role": "assistant", "content": response.content})

            results = []
            for tb in tool_blocks:
                res = await call_mcp_tool(tb.name, tb.input)
                results.append({
                    "type":        "tool_result",
                    "tool_use_id": tb.id,
                    "content":     res,
                })
            claude_messages.append({"role": "user", "content": results})
            continue

        # unexpected stop reason
        raw_text = " ".join(b.text for b in response.content if hasattr(b, "text"))
        reply, actions = parse_actions(raw_text)
        return {"reply": reply or "(no response)", "actions": actions}

    return {"reply": "I hit my tool-call limit on that one. Try rephrasing or breaking the question into steps.", "actions": []}


# ── HTTP endpoints ─────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(request: Request):
    body    = await request.json()
    message = body.get("message", "").strip()
    history = body.get("history", [])
    context = body.get("context", {})

    if not message:
        return JSONResponse({"error": "no message"}, status_code=400)
    if not ANTHROPIC_API_KEY:
        return JSONResponse({
            "reply": "⚠️ No Anthropic API key found. Add ANTHROPIC_API_KEY to your .env file and restart the server.",
            "actions": []
        }, status_code=200)

    messages = []
    for h in history[-12:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    try:
        result = await run_claude(messages, context)
        return JSONResponse(result)
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({
            "reply": f"Something went wrong on my end: {e}\n\nTry again or check the server logs.",
            "actions": []
        }, status_code=200)  # return 200 so the UI still shows the message


@app.get("/api/health")
async def health():
    dd_ok  = bool(DD_API_KEY and DD_APP_KEY)
    ai_ok  = bool(ANTHROPIC_API_KEY)
    tools  = []
    if dd_ok:
        try:
            tools = [t["name"] for t in await get_mcp_tools()]
        except Exception:
            pass
    return {
        "ok":             True,
        "datadog_creds":  dd_ok,
        "anthropic_key":  ai_ok,
        "mcp_tools":      tools,
        "dd_site":        DD_SITE,
    }


if __name__ == "__main__":
    import uvicorn
    print("\n  Bits backend  →  http://localhost:7788")
    print("  Health check  →  http://localhost:7788/api/health\n")
    uvicorn.run(app, host="0.0.0.0", port=7788, log_level="info")
