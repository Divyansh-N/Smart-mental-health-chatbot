from pathlib import Path
from transformers import pipeline

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "emotion_model"

SENTIMENT = {
    "joy": "positive",
    "love": "positive",
    "surprise": "neutral",
    "sadness": "negative",
    "anger": "negative",
    "fear": "negative",
}

MOOD_SCORE = {
    "joy": 1.0, "love": 0.8, "surprise": 0.0,
    "sadness": -0.8, "fear": -0.7, "anger": -0.6,
}

_clf = None


def _get_classifier():
    global _clf
    if _clf is None:
        _clf = pipeline(
            "text-classification",
            model=str(MODEL_DIR),
            tokenizer=str(MODEL_DIR),
            top_k=None,
        )
    return _clf


def predict_emotion(text: str):
    """Return (top_emotion, confidence, sentiment, all_scores)."""
    result = _get_classifier()(text)
    scores = result[0] if isinstance(result[0], list) else result
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)
    top = scores[0]
    return top["label"], float(top["score"]), SENTIMENT[top["label"]], scores


if __name__ == "__main__":
    tests = [
        "I can't sleep, I keep worrying about my exams",
        "I got selected for the internship!",
        "Nobody understands me and I feel so alone",
        "My roommate keeps ignoring me and it makes me furious",
    ]
    for t in tests:
        emotion, conf, sentiment, _ = predict_emotion(t)
        print(f"{emotion} ({conf:.2f}, {sentiment}) -> {t}")