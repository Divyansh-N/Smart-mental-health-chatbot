import re

# Helplines by country. Verify these before your final demo.
HELPLINES = {
    "IN": [
        "Tele-MANAS (24/7, free): 14416",
        "KIRAN Mental Health Helpline: 1800-599-0019",
        "Emergency services: 112",
    ],
    "US": ["988 Suicide & Crisis Lifeline: call or text 988"],
    "UK": ["Samaritans: 116 123 (free, 24/7)"],
}

# Phrases that indicate possible risk of self-harm or suicide.
CRISIS_PATTERNS = [
    r"\bkill (myself|my self)\b",
    r"\bsuicid(e|al)\b",
    r"\bend (my life|it all|everything)\b",
    r"\btake my own life\b",
    r"\b(want|wanna|going) to die\b",
    r"\bwanna die\b",
    r"\bdon'?t want to (live|be alive|be here|exist)\b",
    r"\bbetter off (dead|without me)\b",
    r"\bno reason to (live|go on)\b",
    r"\bnot worth living\b",
    r"\bcan'?t go on\b",
    r"\bwish i (was|were) dead\b",
    r"\bwish i (could )?(disappear|never wake up)\b",
    r"\b(hurt|harm|cut|cutting) (myself|my self)\b",
    r"\bself[- ]?harm\b",
    r"\bhang myself\b",
    r"\boverdose\b",
    # A few Hinglish starters
    r"\bmarna chahta\b",
    r"\bmar jana chahta\b",
    r"\bjeena nahi chahta\b",
    r"\bkhudkushi\b",
]

_COMPILED = [re.compile(p) for p in CRISIS_PATTERNS]


def _normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text).strip()


def check_crisis(text: str) -> bool:
    """Return True if the message contains possible crisis language."""
    t = _normalize(text)
    return any(p.search(t) for p in _COMPILED)


def crisis_response(country: str = "IN") -> str:
    lines = HELPLINES.get(country, HELPLINES["IN"])
    numbers = "\n".join(f"- {line}" for line in lines)
    return (
        "I'm really sorry you're going through this, and I'm glad you told me. "
        "You don't have to face this alone.\n\n"
        "I'm not able to give the kind of help you deserve right now, but trained "
        "people can. Please reach out to one of these right now:\n\n"
        f"{numbers}\n\n"
        "If you're in immediate danger, please call your local emergency number "
        "or go to the nearest hospital. If there's someone you trust nearby, "
        "consider telling them how you feel."
    )


if __name__ == "__main__":
    tests = [
        "I want to kill myself",
        "i dont want to live anymore",
        "Everyone would be better off without me",
        "I'm so stressed about my exams",
        "I got selected for the internship!",
    ]
    for t in tests:
        print(check_crisis(t), "->", t)