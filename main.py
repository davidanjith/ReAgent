from fastapi import FastAPI, HTTPException
from core_agent.summary_pipeline import summarize_topic

app = FastAPI()

@app.post("/summarize/")
async def summarize_topic_route(user_input: str):
    try:
        result = summarize_topic(user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to ReAgent API!"}
