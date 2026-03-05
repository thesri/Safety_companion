from collections import deque

# store last 6 sentences
# context_buffer = deque(maxlen=6)
risk_history = deque(maxlen=6)
from datetime import datetime

context_memory = []

def add_to_context(report):

    entry = {
        "text": report["text"],
        "risk": report["riskscore"],
        "emotion": report["emotion"],
        "time": datetime.now().strftime("%H:%M:%S")
    }

    context_memory.append(entry)

    if len(context_memory) > 10:
        context_memory.pop(0)

def get_context():
    return list(context_memory)

def clear_context():
    context_memory.clear()

def add_risk(score):
    risk_history.append(score)

def get_risk_trend():
    return list(risk_history)