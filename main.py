from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

app = FastAPI(title="Mock Interview API", version="1.1")

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
    raise ValueError("Missing OpenAI API key.")
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

def get_available_chat_models():
    """Fetches the list of available OpenAI models and selects the first available chat completion model."""
    try:
        models = openai.models.list()
        model_list = [model.id for model in models.data if "gpt" in model.id]  # Filter for GPT models
        print("🔍 Available Models:", model_list)

        # Prioritize known chat models
        for model in ["gpt-4.5-preview", "gpt-4o", "gpt-3.5-turbo"]:
            if model in model_list:
                print(f"✅ Using model: {model}")
                return model

        if model_list:
            print(f"⚠️ Using fallback model: {model_list[0]}")
            return model_list[0]

        raise ValueError("No chat-compatible OpenAI models found.")
    except openai.OpenAIError as e:
        print(f"❌ Error fetching OpenAI models: {e}")
        raise HTTPException(status_code=500, detail="Error fetching available OpenAI models.")

@app.post("/api/analyze", response_model=dict)
async def analyze_response(request: InterviewRequest):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is missing.")

    try:
        prompt = f"Question: {request.question}\nAnswer: {request.answer}\n\nEvaluate the response based on clarity, completeness, and professionalism. Provide constructive feedback."

        # Dynamically get the correct model
        model_to_use = get_available_chat_models()

        response = openai.ChatCompletion.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": "You are an expert interviewer evaluating responses for a claims adjuster role."},
                {"role": "user", "content": prompt}
            ]
        )

        feedback = response["choices"][0]["message"]["content"]
        return {"feedback": feedback}

    except openai.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid OpenAI API key. Please check your credentials.")
    except openai.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded. Try again later.")
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
