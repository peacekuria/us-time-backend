# serializers.py
"""Turn ORM rows into the exact dictionaries the API hands to the client.

Keeping this in one place means the response contract is defined once instead
of being implied by whatever attributes each model happens to expose.
"""

from typing import Any, Dict, List, Sequence

from models import Disorder, Question


def serialize_disorder(disorder: Disorder) -> Dict[str, Any]:
    """Flatten a disorder and its remedies into the shape the UI expects."""
    return {
        "id": disorder.id,
        "name": disorder.name,
        "description": disorder.description,
        "symptoms": disorder.symptoms,
        "remedies": [remedy.title for remedy in disorder.remedies],
    }


def serialize_disorders(disorders: Sequence[Disorder]) -> List[Dict[str, Any]]:
    """Serialize a collection of disorders."""
    return [serialize_disorder(disorder) for disorder in disorders]


def serialize_question(question: Question) -> Dict[str, Any]:
    """Serialize one assessment question."""
    return {
        "id": question.id,
        "text": question.text,
        "category": question.category,
        "weight": question.weight,
        "order_index": question.order_index,
    }


def serialize_questions(questions: Sequence[Question]) -> List[Dict[str, Any]]:
    """Serialize a collection of assessment questions."""
    return [serialize_question(question) for question in questions]
