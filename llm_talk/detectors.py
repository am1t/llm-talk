"""Loop detection for AI conversations."""

import re
from difflib import SequenceMatcher


def detect_conversation_loop(
    conversation_turns: list[dict], window_size: int = 5
) -> tuple[bool, str]:
    """Detect if conversation has fallen into a repetitive loop.

    Args:
        conversation_turns: List of conversation turn dicts with 'response' and 'agent' keys.
        window_size: Number of recent turns to analyze.

    Returns:
        Tuple of (is_loop_detected, reason).
    """
    if len(conversation_turns) < window_size:
        return False, ""

    recent_turns = conversation_turns[-window_size:]
    responses = [turn["response"].lower() for turn in recent_turns]

    # Check for goodbye/farewell loops
    farewell_keywords = [
        r"\bgoodbye\b", r"\bbye\b", r"\bfarewell\b",
        r"\btake care\b", r"\bsee you\b", r"\bsigning off\b",
        r"\bending\b", r"\bconcluding\b", r"\bwrap up\b",
        r"\bfinishing up\b", r"\bthat concludes\b",
    ]
    farewell_count = sum(
        1 for resp in responses
        if any(re.search(kw, resp, re.IGNORECASE) for kw in farewell_keywords)
    )
    if farewell_count >= 3:
        return True, "Detected goodbye/farewell loop"

    # Check for repetitive short responses
    avg_length = sum(len(resp.split()) for resp in responses) / len(responses)
    if avg_length < 15:
        unique_responses = len(set(responses))
        if unique_responses <= 2:
            return True, "Detected repetitive short responses"

    # Check for back-and-forth repetitive pattern
    if len(recent_turns) >= 4:
        agents = [turn["agent"] for turn in recent_turns[-4:]]
        last_4 = [turn["response"].lower() for turn in recent_turns[-4:]]

        if agents[0] == agents[2] and agents[1] == agents[3]:
            sim_1 = SequenceMatcher(None, last_4[0], last_4[2]).ratio()
            sim_2 = SequenceMatcher(None, last_4[1], last_4[3]).ratio()
            if sim_1 > 0.7 or sim_2 > 0.7:
                return True, "Detected back-and-forth repetitive pattern"

    return False, ""
