# schemas.py
"""Pydantic request and response models for the US Time API.

The response shapes here mirror what the React frontend renders, so the two
halves of the app agree on field names:

* ``DisorderOut.remedies`` is a list of plain strings because the UI prints
  each remedy directly inside a list item.
* ``AssessmentResult`` carries ``severity`` (low/medium/high) because the UI
  keys its colour scheme off that value.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DisorderSchema(BaseModel):
    """Payload accepted when creating or updating a disorder."""

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    symptoms: str = ""


class DisorderOut(BaseModel):
    """A disorder as returned to the client, remedies flattened to titles."""

    id: int
    name: str
    description: str
    symptoms: Optional[str] = None
    remedies: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class AssessmentSchema(BaseModel):
    """Payload accepted by the raw assessment CRUD endpoints."""

    session_id: str
    answers: str
    result: str
    severity_score: int
    disorder_id: int


class AssessmentAnswersIn(BaseModel):
    """What the client posts when submitting the questionnaire.

    Only the answers are required; the server owns scoring and session
    generation. ``session_id`` may be supplied to resume an existing session.
    """

    answers: List[str] = Field(..., min_length=1)
    session_id: Optional[str] = None


class AssessmentResult(BaseModel):
    """The scored assessment returned to the client for rendering."""

    session_id: str
    result: str
    severity: str
    severity_score: int
    remedies: List[str]
