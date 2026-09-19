# Smart Mental Health Support Chatbot

A chatbot that detects emotions with NLP and sentiment analysis, replies with empathy,
and tracks mood over time. It is a support tool, not a therapist.

## Features
- Rule-based crisis detection with helpline numbers (runs first and overrides everything)
- Emotion detection using a fine-tuned DistilBERT (93% accuracy, 0.88 macro F1 on dair-ai/emotion)
- Empathetic replies from a local LLM (Llama 3.2 via Ollama), with a template fallback
- Mood tracker (stores only mood scores and timestamps, never messages)
- Calm tools: breathing, 5-4-3-2-1 grounding, journaling

## Setup
1. Install Python 3.11 and Ollama, then run `ollama pull llama3.2:3b`
2. Create a virtual environment and run `pip install -r requirements.txt`
3. Put the trained model in `models/emotion_model/` (not included in this repo because of its size)
4. Run `python -m streamlit run app.py`

## Disclaimer
Not a substitute for professional care. In a crisis, contact a helpline or emergency services.