import random

RESPONSES = {
    "sadness": [
        "I'm sorry you're feeling this way. It's okay to feel sad, and you don't have to hide it here. Do you want to tell me more about what's been weighing on you?",
        "That sounds really heavy. Thank you for sharing it with me. What has been the hardest part of it?",
        "Feeling low can be exhausting. You're not alone in this. What do you think is behind it right now?",
    ],
    "fear": [
        "It sounds like you're feeling anxious or scared, and that's a hard place to be. Let's take it one step at a time. What's worrying you the most?",
        "Worry can feel overwhelming, but you're handling it by talking about it. What is the biggest thing on your mind right now?",
        "I hear that you're feeling uneasy. Your feelings make sense. Would it help to break the problem into smaller pieces?",
    ],
    "anger": [
        "It sounds like something really frustrated you. Your feelings are valid. What happened?",
        "That sounds upsetting. It's okay to feel angry. Do you want to talk through what triggered it?",
        "I can hear how frustrated you are. Sometimes writing it out helps. What do you wish had gone differently?",
    ],
    "joy": [
        "That's wonderful to hear! I'm glad you're feeling good. What made today special?",
        "It's great that you're feeling positive. Enjoy it! What's been going well for you?",
        "Love that for you. Taking a moment to notice good feelings helps them last. Tell me more!",
    ],
    "love": [
        "That sounds warm and meaningful. Connection is such an important part of wellbeing. Who or what is making you feel this way?",
        "It's lovely to hear that. Feeling cared for or caring for someone is powerful. Would you like to share more?",
    ],
    "surprise": [
        "That sounds unexpected! How are you feeling about it now?",
        "Wow, sounds like something caught you off guard. What happened?",
    ],
}

NEUTRAL = [
    "Thanks for sharing that with me. I'm here to listen. Can you tell me a little more about how you're feeling?",
    "I want to understand you better. How has your day or week been emotionally?",
]

# (tool name, short instruction). The app will open the matching tool.
COPING = {
    "sadness": ("Journaling prompt", "Write down three things on your mind, then one small thing you can do for yourself today."),
    "fear": ("Breathing exercise", "Breathe in for 4 seconds, hold for 4, breathe out for 6. Repeat 5 times."),
    "anger": ("Grounding exercise (5-4-3-2-1)", "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."),
    "joy": ("Gratitude note", "Write down one thing you're grateful for today."),
    "love": ("Gratitude note", "Write a short message to someone who matters to you."),
    "surprise": ("Grounding exercise (5-4-3-2-1)", "Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."),
}

CONFIDENCE_THRESHOLD = 0.50


def get_reply(emotion: str, confidence: float):
    """Return (reply_text, coping_tool_or_None)."""
    if confidence < CONFIDENCE_THRESHOLD or emotion not in RESPONSES:
        return random.choice(NEUTRAL), None
    return random.choice(RESPONSES[emotion]), COPING.get(emotion)


if __name__ == "__main__":
    for emo, conf in [("sadness", 0.95), ("fear", 0.91), ("joy", 0.51), ("anger", 0.40)]:
        reply, tool = get_reply(emo, conf)
        print(f"[{emo}, {conf}] {reply}")
        print("   Tool:", tool)