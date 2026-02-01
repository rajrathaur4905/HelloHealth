from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow your frontend to communicate with this backend
# In a local development environment, your frontend is likely running from a file URL or a different port.
# For production, replace "http://127.0.0.1:5500" with your actual frontend domain.
origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # Example for Live Server extension in VS Code
    "http://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For now, allow all origins for easy testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the data we expect from the frontend
class SymptomInput(BaseModel):
    symptoms: str

# Load the Hugging Face model
# NOTE: This model is for general text classification. For a real medical app,
# you would need a specialized medical LLM.
try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    print("Hugging Face model loaded successfully.")
except Exception as e:
    print(f"Error loading Hugging Face model: {e}")
    classifier = None

# A simplified knowledge base for potential conditions and recommendations
knowledge_base = {
    "Headache": {
        "diagnosis": "Tension Headache or Migraine",
        "confidence": 0.95,
        "recommendation": "Rest in a quiet, dark room and take over-the-counter pain relievers like ibuprofen or acetaminophen. If symptoms persist or worsen, consult a doctor."
    },
    "Fever": {
        "diagnosis": "Viral Infection",
        "confidence": 0.90,
        "recommendation": "Stay hydrated, get plenty of rest, and take a fever reducer. If fever is high or lasts more than a few days, see a doctor."
    },
    "Cough": {
        "diagnosis": "Common Cold or Bronchitis",
        "confidence": 0.85,
        "recommendation": "Soothe your throat with warm liquids and cough drops. Avoid irritants like smoke. If cough is severe or you have trouble breathing, seek medical advice."
    },
    "Fatigue": {
        "diagnosis": "Stress or Lack of Sleep",
        "confidence": 0.80,
        "recommendation": "Focus on improving sleep hygiene, managing stress, and maintaining a balanced diet. If fatigue is severe or persistent, it may indicate an underlying condition and a doctor should be consulted."
    },
    "Nausea": {
        "diagnosis": "Food Poisoning or Digestive Upset",
        "confidence": 0.88,
        "recommendation": "Drink clear fluids to stay hydrated. Eat bland foods like crackers and rice. Avoid heavy, greasy, or spicy foods."
    },
    "General Symptoms": {
        "diagnosis": "Unclear",
        "confidence": 0.50,
        "recommendation": "Your symptoms require more specific details. Please consult with a healthcare professional for a proper diagnosis."
    }
}

@app.post("/check-symptoms")
async def check_symptoms(symptom_input: SymptomInput):
    user_symptoms = symptom_input.symptoms.lower()

    # Simple lookup for demonstration
    for key, value in knowledge_base.items():
        if key.lower() in user_symptoms:
            return value

    # If no direct match, use the AI model (or fall back to the general case)
    if classifier:
        candidate_labels = list(knowledge_base.keys())
        results = classifier(user_symptoms, candidate_labels)
        
        # Find the best match from the AI and return its corresponding info
        best_match_label = results['labels'][0]
        return knowledge_base.get(best_match_label, knowledge_base["General Symptoms"])
    
    return knowledge_base["General Symptoms"]