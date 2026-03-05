import json
import subprocess
from context_memory import get_context

def query_llm(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "phi3"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=25
        )

        output = result.stdout.strip()

        if not output:
            print("LLM returned empty response")

        return output

    except Exception as e:
        print("LLM error:", e)
        return None

def allowed_tools(risk_score):

    if risk_score < 2:
        return [
            "log_event",
            "start_recording"
        ]

    elif risk_score < 4.5:
        return [
            "log_event",
            "start_recording",
            "flash_light",
            "fake_call",
            "start_location_tracking"
        ]

    else:
        return [
            "start_location_tracking",
            "send_emergency_alert",
            "trigger_alarm",
            "flash_light",
            "deterrence_voice"
        ]

def context_reasoning(context, report):
    allowed = allowed_tools(report["riskscore"])
    print("its from this")
    context = context

    prompt = f"""
You are a deterministic safety AI assistant.

STRICT RULES:
STRICT RULES:

1. risk_score is a base signal but NOT the only signal.
2. You MUST analyze the text meaning based on the previous context in the report.
3.Dont completely rely on keywords but also think. But dont escalate just because it can be unsafe, escalate if it is unsafe
4. Only escalate risk when the text clearly indicates suspicious or unsafe behaviour.

Risk rules:

risk_score >= 4.5 → DANGER  
risk_score between 2 and 4.5 → SAFE or SUSPICIOUS  
risk_score < 2 → SAFE or SUSPICIOUS ONLY (NEVER DANGER)

If the user explicitly says they are fine or safe,
prefer SAFE.

Conversation history:
{context}

Current report:
{report}

Risk score: {report["riskscore"]}

You may ONLY choose tools from this list:
{allowed}


Respond ONLY in JSON:

{{
"risk_level": "SAFE | SUSPICIOUS | DANGER",
"tools": ["tool1","tool2"],
"reason": "short explanation"
}}
"""
    print("context", context)
    print("report", report)

    response = query_llm(prompt)
    print(response)
    if not response:
        return None

    try:
        clean = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return None