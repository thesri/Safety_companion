### Problem
Women and individuals walking alone often face situations where danger escalates rapidly without immediate support.
Existing safety apps rely on manual triggers, which may not be possible during stressful or threatening situations.
Safety Companion addresses this by continuously monitoring voice signals and contextual cues to detect risk in real time.
The system autonomously activates protective actions such as recording, location tracking, and emergency alerts when danger is detected.
### Decision Log
1. Used a hybrid rule-based + LLM reasoning architecture to reduce hallucinations.
2. Implemented risk scoring using emotion, stress, and keyword signals.
3. Used a local LLM (Phi-3 via Ollama) to preserve privacy and reduce cloud dependency.
4. Built an agent action layer to dynamically trigger safety tools based on risk level.
### Evidence Log
Evidence used to determine risk includes:
• Detected stress levels from emotional analysis  
• Suspicious or dangerous keywords from speech input  
• Escalation patterns from conversation context  
• Sentiment and emotional tone shifts  
• Environmental context captured during monitoring
### Risk Log
Potential risks identified during development:
• False positives triggering unnecessary alerts  
• LLM hallucination during context reasoning  
• Speech-to-text errors affecting risk analysis  
• Latency in local LLM processing
  # Mitigation:
• Deterministic risk rules
• Tool restrictions based on risk score
• Context validation before escalation
### Quick start
1.Clone the repository
2.Install dependencies
3.Install and run the local LLM
ollama pull phi3
4.Start the Safety Companion
python listener.py 
And the wake word to use is "chikki" :)
