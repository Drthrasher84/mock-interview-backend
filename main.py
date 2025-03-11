from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="Mock Interview API", version="1.0")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains (update for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API Key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️ WARNING: OPENAI_API_KEY is not set!")
else:
    print("✅ OpenAI API Key detected.")

openai.api_key = api_key

class InterviewRequest(BaseModel):
    question: str
    answer: str

@app.get("/")
def home():
    return {"message": "Mock Interview API is running!"}

@app.get("/api/check-api-key")
def check_api_key():
    if openai.api_key:
        return {"message": "OpenAI API key is successfully loaded."}
    else:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing.")

@app.post("/api/analyze", response_model=dict)
async def analyze_response(request: InterviewRequest):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing.")

    try:
        print(f"🔍 Received Request: {request}")

        prompt = f"Question: {request.question}\nAnswer: {request.answer}\n\nEvaluate the response based on clarity, completeness, and professionalism. Provide constructive feedback."

        # Use only models that support chat completions
        available_models = ["gpt-4.5-preview", "gpt-4o", "gpt-3.5-turbo"]
        response = None

        for model in available_models:
            try:
                print(f"🔍 Trying model: {model}")
                response = openai.ChatCompletion.create(  # Fix function call
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert interviewer evaluating responses for a claims adjuster role."},
                        {"role": "user", "content": prompt}
                    ]
                )
                print("✅ Response received from OpenAI API.")
                break  # Stop if a model works
            except openai.error.InvalidRequestError:
                print(f"⚠️ Model {model} is unavailable, trying next.")
                continue  # Try the next model if the current one fails

        if not response:
            raise HTTPException(status_code=400, detail="No available OpenAI models found for your API key.")

        feedback = response["choices"][0]["message"]["content"]
        print(f"✅ AI Feedback: {feedback}")
        return {"feedback": feedback}

    except openai.error.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key. Please check your credentials.")
    except openai.error.RateLimitError as e:
        print(f"⏳ Rate Limit Exceeded: {e}")
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded. Try again later.")
    except openai.error.OpenAIError as e:
        print(f"⚠️ OpenAI API Error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        print(f"🚨 Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
