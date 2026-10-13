# scoring.py
"""Severity scoring for the self-assessment questionnaire.

This module is deliberately free of database and framework imports so the
scoring rules can be unit tested on their own.
"""

from typing import Dict, List, Optional, Sequence

# The three severity bands the API and the UI agree on.
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"

# Highest score the UI displays ("Score: X/5").
MAX_SEVERITY_SCORE = 5

# A score at or above these thresholds lands in the matching band.
HIGH_SEVERITY_THRESHOLD = 4
MEDIUM_SEVERITY_THRESHOLD = 2

# Accepted answer values, compared case-insensitively.
ANSWER_YES = "yes"
ANSWER_NO = "no"
ANSWER_UNSURE = "unsure"

# Points are counted in half-units so an "unsure" answer can carry half the
# weight of a "yes" without introducing floats.
POINTS_PER_YES = 2
POINTS_PER_UNSURE = 1
POINTS_PER_UNIT = 2

DEFAULT_WEIGHT = 1

RESULT_MESSAGES: Dict[str, str] = {
    SEVERITY_HIGH: (
        "Based on your responses, professional support is recommended."
    ),
    SEVERITY_MEDIUM: (
        "You're showing some symptoms that may benefit from attention."
    ),
    SEVERITY_LOW: "Your responses suggest you're managing well.",
}

REMEDIES: Dict[str, List[str]] = {
    SEVERITY_HIGH: [
        "Consult with a mental health professional",
        "Consider therapy or counseling",
        "Practice daily self-care routines",
        "Reach out to support networks",
        "Consider medication evaluation with a doctor",
    ],
    SEVERITY_MEDIUM: [
        "Practice mindfulness and meditation",
        "Maintain a consistent daily routine",
        "Engage in regular physical activity",
        "Connect with friends and family",
        "Monitor your symptoms over time",
    ],
    SEVERITY_LOW: [
        "Continue with your current healthy routines",
        "Stay connected with your support system",
        "Practice stress management techniques",
        "Regular mental health check-ins",
        "Help others who may be struggling",
    ],
}

# Recommendations used when a disorder has no remedies recorded yet.
GENERIC_REMEDIES: List[str] = [
    "Speak with a qualified mental health professional",
    "Maintain a steady sleep and activity routine",
    "Stay connected with people you trust",
]

# Reference disorders worth reading about for each severity band, matched by
# name against the disorders table when an assessment is saved.
SUGGESTED_DISORDERS: Dict[str, List[str]] = {
    SEVERITY_HIGH: ["Depression", "Anxiety Disorder", "Bipolar Disorder"],
    SEVERITY_MEDIUM: ["Stress", "Anxiety Disorder", "Insomnia"],
    SEVERITY_LOW: [],
}


def normalize_answer(answer: str) -> str:
    """Return a canonical answer value, tolerating case and stray spaces."""
    if answer is None:
        return ""
    return str(answer).strip().lower()


def score_answers(
    answers: Sequence[str],
    weights: Optional[Sequence[int]] = None,
) -> int:
    """Turn a list of answers into a severity score between 0 and 5.

    A "yes" contributes its full question weight, an "unsure" contributes
    half, and anything else (including "no") contributes nothing. The result
    is capped at ``MAX_SEVERITY_SCORE`` so the UI never shows more than 5.
    """
    half_points = 0

    for index, answer in enumerate(answers):
        weight = DEFAULT_WEIGHT
        if weights is not None and index < len(weights):
            weight = weights[index] or DEFAULT_WEIGHT

        value = normalize_answer(answer)
        if value == ANSWER_YES:
            half_points += POINTS_PER_YES * weight
        elif value == ANSWER_UNSURE:
            half_points += POINTS_PER_UNSURE * weight

    score = half_points // POINTS_PER_UNIT
    return min(score, MAX_SEVERITY_SCORE)


def severity_for_score(score: int) -> str:
    """Map a numeric score onto one of the three severity bands."""
    if score >= HIGH_SEVERITY_THRESHOLD:
        return SEVERITY_HIGH
    if score >= MEDIUM_SEVERITY_THRESHOLD:
        return SEVERITY_MEDIUM
    return SEVERITY_LOW


def remedies_for_severity(severity: str) -> List[str]:
    """Return the suggested actions for a severity band."""
    return REMEDIES.get(severity, GENERIC_REMEDIES)


def suggested_disorder_names(severity: str) -> List[str]:
    """Return the names of reference disorders relevant to a severity band."""
    return SUGGESTED_DISORDERS.get(severity, [])


def build_result(
    answers: Sequence[str],
    weights: Optional[Sequence[int]] = None,
) -> Dict[str, object]:
    """Score ``answers`` and return everything the client renders."""
    score = score_answers(answers, weights)
    severity = severity_for_score(score)

    return {
        "result": RESULT_MESSAGES[severity],
        "severity": severity,
        "severity_score": score,
        "remedies": remedies_for_severity(severity),
    }
