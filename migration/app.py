# app.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# Import database and models
from ..database import engine, get_db
from ..models import Base, Disorder, Remedy, Assessment, Question

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Mental Health Assessment API",
    description="Backend API for mental health assessment and disorder information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== PYDANTIC MODELS ==========

class AssessmentRequest(BaseModel):
    """Request model for assessment submission"""
    answers: List[str]  # ["yes", "no", "unsure", "yes", "no"]

class AssessmentResponse(BaseModel):
    """Response model for assessment results"""
    session_id: str
    result: str
    remedies: List[str]
    severity: str
    severity_score: int

class DisorderResponse(BaseModel):
    """Response model for disorder information"""
    id: int
    name: str
    description: str
    symptoms: Optional[str] = None
    remedies: List[str]

class RemedyResponse(BaseModel):
    """Response model for remedy information"""
    id: int
    title: str
    description: str
    category: Optional[str] = None

class QuestionResponse(BaseModel):
    """Response model for assessment questions"""
    id: int
    text: str
    category: Optional[str] = None

# ========== HELPER FUNCTIONS ==========

def calculate_assessment_result(answers: List[str]) -> dict:
    """Calculate assessment result based on answers"""
    yes_count = sum(1 for answer in answers if answer.lower() == "yes")
    
    if yes_count >= 4:
        return {
            "result": "Based on your responses, you may be experiencing significant symptoms. Professional support is recommended.",
            "severity": "high",
            "severity_score": yes_count,
            "remedies": [
                "Consult with a mental health professional",
                "Consider therapy or counseling",
                "Practice daily self-care routines",
                "Reach out to support networks",
                "Consider medication evaluation with a doctor"
            ]
        }
    elif yes_count >= 2:
        return {
            "result": "You're showing some symptoms that may benefit from attention and self-care.",
            "severity": "medium",
            "severity_score": yes_count,
            "remedies": [
                "Practice mindfulness and meditation",
                "Maintain a consistent daily routine",
                "Engage in regular physical activity",
                "Connect with friends and family",
                "Monitor your symptoms over time"
            ]
        }
    else:
        return {
            "result": "Your responses suggest you're managing well. Continue healthy habits.",
            "severity": "low",
            "severity_score": yes_count,
            "remedies": [
                "Continue with your current healthy routines",
                "Stay connected with your support system",
                "Practice stress management techniques",
                "Regular mental health check-ins",
                "Help others who may be struggling"
            ]
        }

# ========== API ENDPOINTS ==========

@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "message": "Mental Health Assessment API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "assessment": "/api/assessments",
            "disorders": "/api/disorders",
            "questions": "/api/questions"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# ========== ASSESSMENT ENDPOINTS ==========

@app.post("/api/assessments", response_model=AssessmentResponse)
def create_assessment(
    assessment: AssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a mental health assessment
    
    - Receives answers to assessment questions
    - Calculates result and severity
    - Stores assessment in database
    - Returns personalized recommendations
    """
    
    # Validate input
    if not assessment.answers:
        raise HTTPException(status_code=400, detail="Answers are required")
    
    if len(assessment.answers) < 5:
        raise HTTPException(status_code=400, detail="Please answer all questions")
    
    # Calculate result
    result_data = calculate_assessment_result(assessment.answers)
    
    # Generate session ID for anonymous tracking
    session_id = str(uuid.uuid4())
    
    # Create assessment record
    db_assessment = Assessment(
        session_id=session_id,
        answers=assessment.answers,
        result=result_data["result"],
        severity_score=result_data["severity_score"]
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    # Return response
    return AssessmentResponse(
        session_id=session_id,
        result=result_data["result"],
        remedies=result_data["remedies"],
        severity=result_data["severity"],
        severity_score=result_data["severity_score"]
    )

@app.get("/api/assessments/{session_id}")
def get_assessment(session_id: str, db: Session = Depends(get_db)):
    """Get assessment by session ID"""
    assessment = db.query(Assessment).filter(Assessment.session_id == session_id).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment

# ========== DISORDER ENDPOINTS ==========

@app.get("/api/disorders", response_model=List[DisorderResponse])
def get_disorders(db: Session = Depends(get_db)):
    """Get all disorders with their remedies"""
    disorders = db.query(Disorder).all()
    
    result = []
    for disorder in disorders:
        # Get remedies for this disorder
        remedies = db.query(Remedy).filter(Remedy.disorder_id == disorder.id).all()
        remedy_list = [remedy.title for remedy in remedies]
        
        result.append(DisorderResponse(
            id=disorder.id,
            name=disorder.name,
            description=disorder.description,
            symptoms=disorder.symptoms,
            remedies=remedy_list
        ))
    
    return result

@app.get("/api/disorders/{disorder_id}", response_model=DisorderResponse)
def get_disorder(disorder_id: int, db: Session = Depends(get_db)):
    """Get specific disorder by ID"""
    disorder = db.query(Disorder).filter(Disorder.id == disorder_id).first()
    
    if not disorder:
        raise HTTPException(status_code=404, detail="Disorder not found")
    
    # Get remedies for this disorder
    remedies = db.query(Remedy).filter(Remedy.disorder_id == disorder_id).all()
    remedy_list = [remedy.title for remedy in remedies]
    
    return DisorderResponse(
        id=disorder.id,
        name=disorder.name,
        description=disorder.description,
        symptoms=disorder.symptoms,
        remedies=remedy_list
    )

@app.get("/api/disorders/search/{name}")
def search_disorders(name: str, db: Session = Depends(get_db)):
    """Search disorders by name"""
    disorders = db.query(Disorder).filter(Disorder.name.ilike(f"%{name}%")).all()
    
    if not disorders:
        raise HTTPException(status_code=404, detail="No disorders found")
    
    result = []
    for disorder in disorders:
        remedies = db.query(Remedy).filter(Remedy.disorder_id == disorder.id).all()
        remedy_list = [remedy.title for remedy in remedies]
        
        result.append(DisorderResponse(
            id=disorder.id,
            name=disorder.name,
            description=disorder.description,
            symptoms=disorder.symptoms,
            remedies=remedy_list
        ))
    
    return result

# ========== QUESTION ENDPOINTS ==========

@app.get("/api/questions", response_model=List[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    """Get all active assessment questions"""
    questions = db.query(Question).filter(Question.is_active == 1).order_by(Question.order_index).all()
    return questions

# ========== REMEDY ENDPOINTS ==========

@app.get("/api/remedies", response_model=List[RemedyResponse])
def get_remedies(db: Session = Depends(get_db)):
    """Get all remedies"""
    remedies = db.query(Remedy).all()
    return remedies

@app.get("/api/remedies/{remedy_id}", response_model=RemedyResponse)
def get_remedy(remedy_id: int, db: Session = Depends(get_db)):
    """Get specific remedy by ID"""
    remedy = db.query(Remedy).filter(Remedy.id == remedy_id).first()
    
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    
    return remedy

# ========== DATA INITIALIZATION ==========

@app.post("/api/seed-data")
def seed_initial_data(db: Session = Depends(get_db)):
    """Seed database with initial data (for development)"""
    
    # Check if data already exists
    disorder_count = db.query(Disorder).count()
    if disorder_count > 0:
        return {"message": "Data already seeded"}
    
    # Create disorders
    disorders_data = [
        {
            "name": "Depression",
            "description": "A mental health disorder characterized by persistent sadness, loss of interest in activities, and difficulty carrying out daily tasks.",
            "symptoms": "Persistent sadness, hopelessness, loss of interest, sleep disturbances, changes in appetite, fatigue, difficulty concentrating"
        },
        {
            "name": "Anxiety Disorder",
            "description": "Excessive worry, fear, or anxiety that interferes with daily activities and is difficult to control.",
            "symptoms": "Excessive worry, restlessness, fatigue, difficulty concentrating, irritability, muscle tension, sleep problems"
        },
        {
            "name": "Bipolar Disorder",
            "description": "A disorder associated with episodes of mood swings ranging from depressive lows to manic highs.",
            "symptoms": "Mood swings, manic episodes, depressive episodes, racing thoughts, irritability, sleep changes, risk-taking behavior"
        }
    ]
    
    created_disorders = []
    for disorder_data in disorders_data:
        disorder = Disorder(**disorder_data)
        db.add(disorder)
        db.flush()  # Get the ID
        created_disorders.append(disorder)
    
    db.commit()
    
    # Create remedies for each disorder
    remedies_data = [
        # Depression remedies
        {"disorder_id": created_disorders[0].id, "title": "Cognitive Behavioral Therapy", "description": "A type of psychotherapy that helps identify and change negative thought patterns.", "category": "therapy"},
        {"disorder_id": created_disorders[0].id, "title": "Antidepressant Medication", "description": "Medications that can help relieve symptoms of depression.", "category": "medication"},
        {"disorder_id": created_disorders[0].id, "title": "Regular Exercise", "description": "Physical activity releases endorphins and improves mood.", "category": "lifestyle"},
        
        # Anxiety remedies
        {"disorder_id": created_disorders[1].id, "title": "Exposure Therapy", "description": "Gradual exposure to feared situations to reduce anxiety.", "category": "therapy"},
        {"disorder_id": created_disorders[1].id, "title": "Mindfulness Meditation", "description": "Practice focusing on the present moment to reduce worry.", "category": "lifestyle"},
        {"disorder_id": created_disorders[1].id, "title": "Anti-anxiety Medication", "description": "Medications that can help reduce anxiety symptoms.", "category": "medication"},
        
        # Bipolar remedies
        {"disorder_id": created_disorders[2].id, "title": "Mood Stabilizers", "description": "Medications that help control mood swings.", "category": "medication"},
        {"disorder_id": created_disorders[2].id, "title": "Psychoeducation", "description": "Learning about the disorder and developing coping strategies.", "category": "therapy"},
        {"disorder_id": created_disorders[2].id, "title": "Regular Sleep Schedule", "description": "Maintaining consistent sleep patterns to help stabilize mood.", "category": "lifestyle"}
    ]
    
    for remedy_data in remedies_data:
        remedy = Remedy(**remedy_data)
        db.add(remedy)
    
    # Create assessment questions
    questions_data = [
        {"text": "Have you experienced persistent feelings of sadness or hopelessness?", "category": "mood", "weight": 2, "order_index": 1},
        {"text": "Have you lost interest or pleasure in activities you used to enjoy?", "category": "interest", "weight": 2, "order_index": 2},
        {"text": "Have you noticed changes in your appetite or weight?", "category": "appetite", "weight": 1, "order_index": 3},
        {"text": "Do you have trouble sleeping or sleep too much?", "category": "sleep", "weight": 1, "order_index": 4},
        {"text": "Do you often feel tired or lack energy?", "category": "energy", "weight": 1, "order_index": 5}
    ]
    
    for question_data in questions_data:
        question = Question(**question_data)
        db.add(question)
    
    db.commit()
    
    return {"message": "Database seeded successfully", "disorders_added": len(created_disorders)}

# ========== RUN APPLICATION ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)