from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains (update for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch OpenAI API Key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️ WARNING: OPENAI_API_KEY is not set!")

openai.api_key = api_key

class InterviewRequest(BaseModel):
    question: str
    answer: str

@app.get("/")  # Root route to test API is running
def home():
    return {"message": "Mock Interview API is running!"}

@app.get("/api/check-api-key")  # New route to verify API key
def check_api_key():
    if openai.api_key:
        return {"message": "OpenAI API key is successfully loaded."}
    else:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing.")

@app.post("/api/analyze")
async def analyze_response(request: InterviewRequest):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing.")
    
    try:
        prompt = f"Question: {request.question}\nAnswer: {request.answer}\n\nEvaluate the response based on clarity, completeness, and professionalism. Provide constructive feedback."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert interviewer evaluating responses for a claims adjuster role."},
                      {"role": "user", "content": prompt}]
        )
        
        feedback = response["choices"][0]["message"]["content"]
        return {"feedback": feedback}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
