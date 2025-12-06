# 1. import fast api class
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# this is an inbuilt package in python which will allow us to define the shape of POST and PATCH methods and also do validations
from pydantic import BaseModel

from .database import engine, get_db
from .models import Base, Disorder, Remedy, Assessment, Question


# create and instance
app = FastAPI()

# allow network request from all servers
"""
-> by default the server only allows requests comming from the same port but
-> more often the frontend runs on a different port hence we need to allow this by setting
-> allow_origins = ["*"]
-> likewise, we also need to allow all the http methods by setting
-> allow_methods = ["*"]

-> This is not the best thing to do for security
"""
app.add_middleware(CORSMiddleware, allow_origins = ["*"], allow_methods=["*"])

# create routes to access resources
@app.get("/")
def read_root():
    return {"Hello": "World"}

class DisorderSchema(BaseModel):
    name: str
    description: str
    symptoms: str

# http://localhost:8000/disorder -> POST -> create a single disorder
@app.post("/disorder")
def create_disorder(disorder: DisorderSchema, session = Depends(get_db)):
    # check if the disorder exists
    existing = session.query(Disorder).filter(Disorder.name == disorder.name).first()

    if existing is None:
        # persist to db
        # 1. create an instance of the disorder class(model) with the details
        new_disorder = Disorder(name = disorder.name, description=disorder.description, symptoms=disorder.symptoms)
        # 2. add the instance to the transaction
        session.add(new_disorder)
        # 3. commit the transaction
        session.commit()
        # return a message that the disorder has been created
        return {"message": "Disorder created successfully"}
    else:
        return {"message": "Disorder already exists"}

# http://localhost:8000/disorder -> GET -> retrieve all disorders
@app.get("/disorder")
def get_disorders(session = Depends(get_db)):
    # use sql alchemy to retrieve all disorders
    disorders = session.query(Disorder).all()
    return disorders

# http://localhost:8000/disorder/7 -> GET -> get a single disorder
@app.get("/disorder/{disorder_id}")
def get_disorder(disorder_id: int, session: Session = Depends(get_db)):
    # retrieve a single disorder using sqlalchemy
    disorder = session.query(Disorder).filter(Disorder.id == disorder_id).first()
    if not disorder:
        raise HTTPException(status_code=404, detail="Disorder not found")
    return disorder

# http://localhost:8000/disorder/7 -> PATCH -> update a single disorder
@app.patch("/disorder/{disorder_id}")
def update_disorder(disorder_id: int, disorder: DisorderSchema, session: Session = Depends(get_db)):
    existing_disorder = session.query(Disorder).filter(Disorder.id == disorder_id).first()
    if not existing_disorder:
        raise HTTPException(status_code=404, detail="Disorder not found")
    existing_disorder.name = disorder.name
    existing_disorder.description = disorder.description
    existing_disorder.symptoms = disorder.symptoms
    session.commit()
    return {"message": "Disorder updated successfully"}

# http://localhost:8000/disorder/7 -> DELETE -> delete a single disorder
@app.delete("/disorder/{disorder_id}")
def delete_disorder(disorder_id: int, session: Session = Depends(get_db)):
    disorder = session.query(Disorder).filter(Disorder.id == disorder_id).first()
    if not disorder:
        raise HTTPException(status_code=404, detail="Disorder not found")
    session.delete(disorder)
    session.commit()
    return {"message": "Disorder deleted successfully"}

class AssessmentSchema(BaseModel):
    session_id: str
    answers: str  # Simplified as string for now
    result: str
    severity_score: int
    disorder_id: int

# http://localhost:8000/assessment -> POST -> to create assessment
@app.post("/assessment")
def create_assessment(assessment: AssessmentSchema, session = Depends(get_db)):
    # 1. create instance of the model class imported from models.py
    new_assessment = Assessment(
        session_id=assessment.session_id,
        answers=assessment.answers,
        result=assessment.result,
        severity_score=assessment.severity_score,
        suggested_disorder_ids=[assessment.disorder_id]
    )
    # 2. add this to session
    session.add(new_assessment)
    # 3. save it by commiting the transaction
    session.commit()

    return {"message": "Assessment added successfully"}

# http://localhost:8000/assessment -> GET -> retrieve all assessments
@app.get("/assessment")
def get_assessments(session = Depends(get_db)):
    # use sql alchemy to retrieve all assessments
    assessments = session.query(Assessment).all()
    return assessments

# http://localhost:8000/assessment/7 -> GET -> get a single assessment
@app.get("/assessment/{assessment_id}")
def get_assessment(assessment_id: int, session: Session = Depends(get_db)):
    # retrieve a single assessment using sqlalchemy
    assessment = session.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

# http://localhost:8000/assessment/7 -> PATCH -> update a single assessment
@app.patch("/assessment/{assessment_id}")
def update_assessment(assessment_id: int, assessment: AssessmentSchema, session: Session = Depends(get_db)):
    existing_assessment = session.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not existing_assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    existing_assessment.session_id = assessment.session_id
    existing_assessment.answers = assessment.answers
    existing_assessment.result = assessment.result
    existing_assessment.severity_score = assessment.severity_score
    existing_assessment.suggested_disorder_ids = [assessment.disorder_id]
    session.commit()
    return {"message": "Assessment updated successfully"}

# http://localhost:8000/assessment/7 -> DELETE -> delete a single assessment
@app.delete("/assessment/{assessment_id}")
def delete_assessment(assessment_id: int, session: Session = Depends(get_db)):
    assessment = session.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    session.delete(assessment)
    session.commit()
    return {"message": "Assessment deleted successfully"}


