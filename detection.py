import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from huggingface_hub import hf_hub_download
from datetime import datetime
import socket
import shutil
import subprocess
import json
import re
import threading
from queuem import analysis_queue
import os
from action import action_layer
def save_conversation(text):

    os.makedirs("memory", exist_ok=True)

    with open("memory/conversation_log.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
        f.flush()

def query_phi3(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "phi3", prompt],
            capture_output=True,
            text=True,
            encoding='utf-8', 
            errors='ignore',
            timeout=20
        )
        return result.stdout.strip()
    except Exception:
        return None

def ollama_available():
    return shutil.which("ollama") is not None

model_id = "SamLowe/roberta-base-go_emotions-onnx"

tokenizer = AutoTokenizer.from_pretrained(model_id)

onnx_path = hf_hub_download(
    repo_id=model_id,
    filename="onnx/model.onnx"
)

session = ort.InferenceSession(onnx_path)

labels = [
"admiration","amusement","anger","annoyance","approval","caring",
"confusion","curiosity","desire","disappointment","disapproval",
"disgust","embarrassment","excitement","fear","gratitude","grief",
"joy","love","nervousness","optimism","pride","realization","relief",
"remorse","sadness","surprise","neutral"
]

def detect_emotions(text):

    tokens = tokenizer(text, return_tensors="np", truncation=True)

    input_ids = tokens["input_ids"].astype(np.int64)
    attention_mask = tokens["attention_mask"].astype(np.int64)

    outputs = session.run(
        None,
        {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
    )

    logits = outputs[0][0]

    probs = 1 / (1 + np.exp(-logits))

    return {labels[i]: float(probs[i]) for i in range(len(labels))}

danger_words = [
    "help","attack","follow","following","knife","gun","weapon",
    "kidnap","danger","emergency","police","threat",
    "behind","chasing","stalking","blood",
    "scream","dont move","leave me","stop","run", "save", "get away",
    "leave me alone", "stop following me", 
]

suspicious_words = [
    "where are you",
    "are you alone",
    "come outside",
    "send location",
    "dont tell anyone",
    "open the door",
    "wait there"
]

stress_words = [
    "please","hurry","fast","scared","afraid","panic",
    "worried","nervous","help me"
]

def detect_keywords(text):
    text = text.lower()
    result = {
        "danger": [],
        "suspicious": [],
        "stress": []
    }
    for w in danger_words:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            result["danger"].append(w)
    for w in suspicious_words:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            result["suspicious"].append(w)

    for w in stress_words:
        if re.search(r"\b" + re.escape(w) + r"\b", text):
            result["stress"].append(w)

    return result

def compute_stress(emotions):

    fear = emotions.get("fear", 0)
    anger = emotions.get("anger", 0)
    sadness = emotions.get("sadness", 0)
    joy = emotions.get("joy", 0)

    stress_score = (
        fear * 5 +
        anger * 3 +
        sadness * 2 -
        joy * 2
    )

    return round(stress_score, 3)

def compute_risk(keywords, stress_score):

    danger_score = len(keywords["danger"]) * 5
    suspicious_score = len(keywords["suspicious"]) * 3
    stress_word_score = len(keywords["stress"]) * 1

    keyword_score = danger_score + suspicious_score + stress_word_score

    stress_component = max(stress_score, 0) * 2

    risk_score = keyword_score + stress_component

    if risk_score >= 4.5:
        level = "DANGER"
    elif risk_score >= 3:
        level = "SUSPICIOUS"
    else:
        level = "SAFE"

    return round(risk_score, 3), level

def analyze_text(text):

    print("\nINPUT:", text)

    emotions = detect_emotions(text)
    keywords = detect_keywords(text)
    stress = compute_stress(emotions)

    risk_score, level = compute_risk(keywords, stress)

    top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:5]

    print("\nTop Emotions:")
    for e, v in top_emotions:
        print(e, round(v,3))

    print("\nStress Score:", stress)

    print("\nKeyword Detection:")
    print(keywords)

    print("\nRisk Score:", risk_score)
    print("Risk Level:", level)

    print("\n-------------------------")

    return {
        "text": text,
        "emotions": emotions,
        "stress_score": stress,
        "keywords": keywords,
        "risk_score": risk_score,
        "risk_level": level
    }

def internet_avail():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        print("true")
        return True
    except OSError:
        return False

def build_report(text,emotions,stress,keywords):
    top_emotion = max(emotions, key=emotions.get)
    risk_score, level = compute_risk(keywords, stress)
    report = {
        "text":text,
        "stress": stress,
        "emotion": top_emotion,
        "keywords": keywords,
        "riskscore": risk_score,
        "risklevel": level,
        "location_risk": "unknown",
        "time": datetime.now().strftime("%H:%M:%S")
    }
    return report

def offline_brain(report):
    risk = report.get("riskscore", 0)

    if risk >= 4.5:
        return {"risk_level": "HIGH", "action": "ALERT"}
    elif risk > 3:
        return {"risk_level": "MEDIUM", "action": "MONITOR"}
    else:
        return {"risk_level": "LOW", "action": "ALLOW"}

def online_brain(report):

    prompt = f"""
        You are a safety AI.

        Analyze the situation and respond ONLY in JSON.

        Report:
        {report}

        Format:
        {{
        "risk_level": "SAFE | SUSPICIOUS | DANGER",
        "action": "LOG | MONITOR | ALERT",
        "reason": "short explanation"
        }}
        """
    response = query_phi3(prompt)

    if not response:
        return offline_brain(report)

    try:
        return json.loads(response)
    except:
        return {"raw_llm_output": response}

def agent_brain(report):
    risk = report["riskscore"]
    print("risk<=4.5 using llm")
    if risk >= 4.5:
        return offline_brain(report)

    if ollama_available():
        return online_brain(report)

    return offline_brain(report)

def analyze_texts(text):

    emotions = detect_emotions(text)

    keywords = detect_keywords(text)

    stress = compute_stress(emotions)

    risk_score, rule_level = compute_risk(keywords, stress)

    report = build_report(text, emotions, stress, keywords)

    decision = agent_brain(report)

    print("\nStress Score:", stress)

    print("\nKeyword Detection:")
    print(keywords)

    print("\nRisk Score:", risk_score)
    print("\nRisk Level:", rule_level)

    print("\nagent decision", decision)
    result = {
        "report": report,
        "risk_score": risk_score,
        "rule_level": rule_level,
        "agent_decision": decision
    }

    return result

def ai_worker():
    while True:
        text = analysis_queue.get()

        if text is None:
            break
        
        print("\n[Worker received]:", text)
        save_conversation(text)
        result = analyze_texts(text)
        print("\n AI Result")
        print(json.dumps(result,indent=2))
        decision = result["agent_decision"]
        report = result["report"]
        action_layer(decision, report)
        analysis_queue.task_done()

def start_ai_worker():
    threading.Thread(target=ai_worker, daemon=True).start()