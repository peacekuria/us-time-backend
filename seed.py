# seed.py
"""Idempotent database seeding.

The API calls :func:`seed_database` on startup. Every step checks for existing
rows first, so restarting the server never duplicates content and never
overwrites edits made through the API.
"""

from sqlalchemy.orm import Session

from models import Disorder, Question, Remedy
from seed_data import DISORDERS, QUESTIONS


def _seed_questions(session: Session) -> int:
    """Insert any questionnaire questions that are missing."""
    created = 0

    for question in QUESTIONS:
        exists = (
            session.query(Question)
            .filter(Question.text == question["text"])
            .first()
        )
        if exists is not None:
            continue

        session.add(
            Question(
                text=question["text"],
                category=question["category"],
                order_index=question["order_index"],
            )
        )
        created += 1

    return created


def _seed_disorders(session: Session) -> int:
    """Insert any disorders that are missing, together with their remedies."""
    created = 0

    for entry in DISORDERS:
        exists = (
            session.query(Disorder)
            .filter(Disorder.name == entry["name"])
            .first()
        )
        if exists is not None:
            continue

        disorder = Disorder(
            name=entry["name"],
            description=entry["description"],
            symptoms=entry["symptoms"],
        )

        for title, description, category in entry["remedies"]:
            disorder.remedies.append(
                Remedy(title=title, description=description, category=category)
            )

        session.add(disorder)
        created += 1

    return created


def seed_database(session: Session) -> dict:
    """Ensure the reference data exists and return a count of what was added."""
    added_questions = _seed_questions(session)
    added_disorders = _seed_disorders(session)

    if added_questions or added_disorders:
        session.commit()

    return {
        "questions": added_questions,
        "disorders": added_disorders,
    }
