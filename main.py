from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
from models import LogisticRegression

# Define the FastAPI app
app = FastAPI()

# Pydantic model for data validation
class StudentData(BaseModel):
    age_at_enrollment: int
    gender: int
    scholarship_holder: int
    curricular_units_1st_sem_enrolled: int
    curricular_units_1st_sem_approved: int
    curricular_units_1st_sem_grade: float
    curricular_units_2nd_sem_enrolled: int
    curricular_units_2nd_sem_approved: int
    curricular_units_2nd_sem_grade: float
    debtor: int
    tuition_fees_up_to_date: int

# Global variables for models and scaler
model = None
scaler = None
feature_order = None

# Define the order of features to match the model's training data (move to global scope)
continuous_features = [
    "age_at_enrollment", "curricular_units_1st_sem_enrolled", "curricular_units_1st_sem_approved", 
    "curricular_units_1st_sem_grade", "curricular_units_2nd_sem_enrolled", 
    "curricular_units_2nd_sem_approved", "curricular_units_2nd_sem_grade",
    "tuition_fees_up_to_date"
]
binary_features = ["gender", "scholarship_holder", "debtor"]
feature_order = continuous_features + binary_features

# Use FastAPI lifespan event handler instead of deprecated on_event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler
    try:
        with open("logistic_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        print("Models loaded successfully!")
    except FileNotFoundError:
        print("Model or scaler file not found. Please ensure 'logistic_model.pkl' and 'scaler.pkl' are in the project directory.")
        model, scaler = None, None
    yield

app = FastAPI(lifespan=lifespan)

# Define the prediction endpoint
@app.post("/predict-and-recommend")
async def predict_and_recommend(student_data: StudentData):
    if not model or not scaler:
        return {"error": "Models are not loaded. Please check the server logs."}

    # Convert the Pydantic model to a dictionary and then to a NumPy array
    student_dict = student_data.model_dump()
    features = [student_dict[feat] for feat in feature_order]
    features = np.array(features).reshape(1, -1)

    # Scale the continuous features
    continuous_idx = list(range(len(continuous_features)))
    features_scaled = features.astype(float).copy()
    features_scaled[:, continuous_idx] = scaler.transform(features[:, continuous_idx])

    # Predict the risk score and label
    prob = model.predict_prob(features_scaled)[0]
    prediction = 1 if prob > 0.5 else 0
    prediction_label = "Dropout" if prediction == 1 else "Enrolled/Graduate"

    # Generate recommendations based on the prediction
    recommendations = ["Attend mentoring sessions", "Seek academic counseling"] if prediction == 1 else ["Keep up the good work!"]

    # Create and return the final JSON response
    response = {
        "risk_score": round(float(prob), 2),
        "prediction_label": prediction_label,
        "recommended_resources": recommendations
    }

    return response