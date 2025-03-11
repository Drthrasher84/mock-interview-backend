from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

class InterviewRequest(BaseModel):
    question: str
    answer: str

@app.post("/api/analyze")
async def analyze_response(request: InterviewRequest):
    try:
        prompt = f"Question: {request.question}\\nAnswer: {request.answer}\\n\\nEvaluate the response based on clarity, completeness, and professionalism. Provide constructive feedback."
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert interviewer evaluating responses for a claims adjuster role."},
                      {"role": "user", "content": prompt}]
        )
        
        feedback = response["choices"][0]["message"]["content"]
        return {"feedback": feedback}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
