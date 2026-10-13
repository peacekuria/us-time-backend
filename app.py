# app.py
"""HTTP entry point for the US Time mental health API.

Route groups:
    /                        liveness probe
    /health                  liveness probe
    /api/questions           the assessment questionnaire
    /api/disorders[...]      reference information about disorders
    /api/assessments[...]    scored submissions, used by the React client
    /assessment[...]         raw assessment CRUD
"""

from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Assessment, Disorder, Question
from schemas import (
    AssessmentAnswersIn,
    AssessmentResult,
    AssessmentSchema,
    DisorderOut,
    DisorderSchema,
)
from scoring import build_result, suggested_disorder_names
from seed import seed_database
from serializers import (
    serialize_disorder,
    serialize_disorders,
    serialize_questions,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create tables and load reference data before the first request."""
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()

    yield


app = FastAPI(title="US Time API", version="1.0.0", lifespan=lifespan)

# The Vite dev server runs on a different port than the API, so browser
# requests need permissive CORS. This is fine for local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ordered_questions(session: Session) -> List[Question]:
    """Return the active questionnaire in display order."""
    return (
        session.query(Question)
        .order_by(Question.order_index)
        .all()
    )


def _question_weights(questions: List[Question]) -> Optional[List[int]]:
    """Extract scoring weights, or None when there are no questions."""
    if not questions:
        return None
    return [
        question.weight if question.weight is not None else 1
        for question in questions
    ]


def _disorder_ids_for_names(session: Session, names: List[str]) -> List[int]:
    """Look up disorder ids by name, ignoring names that are not seeded."""
    if not names:
        return []

    rows = session.query(Disorder).filter(Disorder.name.in_(names)).all()
    return [row.id for row in rows]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/questions")
def get_questions(session: Session = Depends(get_db)):
    """Return every assessment question in display order."""
    return serialize_questions(_ordered_questions(session))


@app.post(
    "/api/disorders",
    response_model=DisorderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_disorder(disorder: DisorderSchema, session: Session = Depends(get_db)):
    """Create a disorder, rejecting a name that is already in use."""
    existing = (
        session.query(Disorder)
        .filter(Disorder.name == disorder.name)
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A disorder with that name already exists",
        )

    new_disorder = Disorder(
        name=disorder.name,
        description=disorder.description,
        symptoms=disorder.symptoms,
    )
    session.add(new_disorder)
    session.commit()
    session.refresh(new_disorder)

    return serialize_disorder(new_disorder)


@app.get("/api/disorders", response_model=List[DisorderOut])
def get_disorders(session: Session = Depends(get_db)):
    """Return every disorder with its treatment options."""
    disorders = session.query(Disorder).order_by(Disorder.name).all()
    return serialize_disorders(disorders)


# Declared before /api/disorders/{disorder_id} so the literal "search"
# segment is not swallowed by the integer path parameter.
@app.get("/api/disorders/search/{name}", response_model=List[DisorderOut])
def search_disorders(name: str, session: Session = Depends(get_db)):
    """Search disorders by name, description or symptoms (case-insensitive)."""
    term = f"%{name.strip().lower()}%"

    disorders = (
        session.query(Disorder)
        .filter(
            Disorder.name.ilike(term)
            | Disorder.description.ilike(term)
            | Disorder.symptoms.ilike(term)
        )
        .order_by(Disorder.name)
        .all()
    )
    return serialize_disorders(disorders)


@app.get("/api/disorders/{disorder_id}", response_model=DisorderOut)
def get_disorder(disorder_id: int, session: Session = Depends(get_db)):
    """Return a single disorder."""
    disorder = (
        session.query(Disorder)
        .filter(Disorder.id == disorder_id)
        .first()
    )
    if disorder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found",
        )

    return serialize_disorder(disorder)


@app.patch("/api/disorders/{disorder_id}", response_model=DisorderOut)
def update_disorder(
    disorder_id: int,
    disorder: DisorderSchema,
    session: Session = Depends(get_db),
):
    """Update an existing disorder."""
    existing = (
        session.query(Disorder)
        .filter(Disorder.id == disorder_id)
        .first()
    )
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found",
        )

    existing.name = disorder.name
    existing.description = disorder.description
    existing.symptoms = disorder.symptoms
    session.commit()
    session.refresh(existing)

    return serialize_disorder(existing)


@app.delete("/api/disorders/{disorder_id}")
def delete_disorder(disorder_id: int, session: Session = Depends(get_db)):
    """Delete a disorder and its treatment options."""
    disorder = (
        session.query(Disorder)
        .filter(Disorder.id == disorder_id)
        .first()
    )
    if disorder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found",
        )

    session.delete(disorder)
    session.commit()

    return {"message": "Disorder deleted successfully"}


@app.post("/api/assessments", response_model=AssessmentResult)
def submit_assessment(
    payload: AssessmentAnswersIn,
    session: Session = Depends(get_db),
):
    """Score submitted answers, store the result and return it.

    Reusing a ``session_id`` updates that assessment instead of inserting a
    second row, so a repeated submission does not fail on the unique index.
    """
    questions = _ordered_questions(session)
    outcome = build_result(payload.answers, _question_weights(questions))
    severity = str(outcome["severity"])

    session_id = payload.session_id or str(uuid4())
    suggested_ids = _disorder_ids_for_names(
        session, suggested_disorder_names(severity)
    )

    record = (
        session.query(Assessment)
        .filter(Assessment.session_id == session_id)
        .first()
    )
    if record is None:
        record = Assessment(session_id=session_id)
        session.add(record)

    record.answers = list(payload.answers)
    record.result = severity
    record.severity_score = outcome["severity_score"]
    record.suggested_disorder_ids = suggested_ids
    session.commit()

    return AssessmentResult(session_id=session_id, **outcome)


@app.get("/api/assessments/{session_id}", response_model=AssessmentResult)
def get_assessment(session_id: str, session: Session = Depends(get_db)):
    """Return a previously stored assessment by its session id."""
    record = (
        session.query(Assessment)
        .filter(Assessment.session_id == session_id)
        .first()
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    stored_answers = record.answers if isinstance(record.answers, list) else []
    questions = _ordered_questions(session)
    outcome = build_result(stored_answers, _question_weights(questions))

    return AssessmentResult(session_id=session_id, **outcome)


@app.post("/assessment")
def create_assessment(
    assessment: AssessmentSchema,
    session: Session = Depends(get_db),
):
    """Store an assessment exactly as supplied by the caller."""
    new_assessment = Assessment(
        session_id=assessment.session_id,
        answers=assessment.answers,
        result=assessment.result,
        severity_score=assessment.severity_score,
        suggested_disorder_ids=[assessment.disorder_id],
    )
    session.add(new_assessment)
    session.commit()

    return {"message": "Assessment added successfully"}


@app.get("/assessment")
def get_assessments(session: Session = Depends(get_db)):
    """Return every stored assessment."""
    return session.query(Assessment).all()


@app.get("/assessment/{assessment_id}")
def get_assessment_by_id(
    assessment_id: int,
    session: Session = Depends(get_db),
):
    """Return a single stored assessment by its primary key."""
    assessment = (
        session.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return assessment


@app.patch("/assessment/{assessment_id}")
def update_assessment(
    assessment_id: int,
    assessment: AssessmentSchema,
    session: Session = Depends(get_db),
):
    """Replace the fields of a stored assessment."""
    existing = (
        session.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    existing.session_id = assessment.session_id
    existing.answers = assessment.answers
    existing.result = assessment.result
    existing.severity_score = assessment.severity_score
    existing.suggested_disorder_ids = [assessment.disorder_id]
    session.commit()

    return {"message": "Assessment updated successfully"}


@app.delete("/assessment/{assessment_id}")
def delete_assessment(
    assessment_id: int,
    session: Session = Depends(get_db),
):
    """Delete a stored assessment."""
    assessment = (
        session.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    session.delete(assessment)
    session.commit()

    return {"message": "Assessment deleted successfully"}
