import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"   # use "llama3.2:1b" if your laptop is slow

SYSTEM_PROMPT = """You are a warm, supportive listener for a student mental health support app.
Rules:
- Reply in 2 to 4 short sentences, in simple, natural language.
- Acknowledge the user's feelings first, then ask ONE gentle follow-up question.
- Never diagnose, never name mental illnesses as a diagnosis, never suggest medication.
- Don't give long lists or lectures. Don't say "as an AI".
- If the problem sounds serious or ongoing, gently suggest talking to a counsellor or someone they trust.
- You are a support tool, not a therapist."""


def generate_reply(history, emotion, confidence):
    """Return the LLM reply as text, or None if the LLM isn't available."""
    system = SYSTEM_PROMPT
    if confidence >= 0.5:
        system += (f"\n\nAn emotion classifier detected that the user's latest message "
                   f"expresses: {emotion}. Use this only as a hint, don't mention it.")
    messages = [{"role": "system", "content": system}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": False,
                  "options": {"temperature": 0.7, "num_predict": 150}},
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except Exception:
        return None


if __name__ == "__main__":
    test = [{"role": "user", "content": "I'm so stressed about my exams"}]
    print(generate_reply(test, "fear", 0.91))