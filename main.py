from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core_agent.summary_pipeline import summarize_topic

app = FastAPI()

class SummarizeRequest(BaseModel):
    user_input: str

@app.post("/summarize/")
async def summarize_topic_route(request: SummarizeRequest):
    try:
        result = summarize_topic(request.user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to ReAgent API!"}
