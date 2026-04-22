from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# ROOT route (for browser testing)
@app.get("/")
def home():
    return {"message": "Voting API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = {"polls": []}

def generate_id():
    return str(int(time.time() * 1000))


# GET all polls
@app.get("/polls")
def get_polls():
    return db["polls"]


# CREATE poll
@app.post("/polls")
async def create_poll(data: dict):
    question = data.get("question")
    options = data.get("options")

    if not question or not options or not (2 <= len(options) <= 4):
        return {"error": "Invalid input (2–4 options required)"}

    poll = {
        "id": generate_id(),
        "question": question,
        "options": [{"text": opt, "votes": 0} for opt in options],
        "voters": [],
        "createdAt": time.time()
    }

    db["polls"].append(poll)
    return poll


# VOTE
@app.post("/polls/{poll_id}/vote")
async def vote(poll_id: str, request: Request):
    body = await request.json()
    option_index = body.get("optionIndex")

    poll = next((p for p in db["polls"] if p["id"] == poll_id), None)

    if not poll:
        return {"error": "Poll not found"}

    user_ip = request.client.host

    if user_ip in poll["voters"]:
        return {"error": "You already voted"}

    if option_index is None or option_index < 0 or option_index >= len(poll["options"]):
        return {"error": "Invalid option"}

    poll["options"][option_index]["votes"] += 1
    poll["voters"].append(user_ip)

    return poll


# DELETE poll
@app.delete("/polls/{poll_id}")
def delete_poll(poll_id: str):
    db["polls"] = [p for p in db["polls"] if p["id"] != poll_id]
    return {"message": "Poll deleted successfully"}


# GET results
@app.get("/polls/{poll_id}/results")
def get_results(poll_id: str):
    poll = next((p for p in db["polls"] if p["id"] == poll_id), None)

    if not poll:
        return {"error": "Poll not found"}

    total_votes = sum(o["votes"] for o in poll["options"])

    results = []
    for o in poll["options"]:
        percentage = (o["votes"] / total_votes * 100) if total_votes else 0
        results.append({
            "text": o["text"],
            "votes": o["votes"],
            "percentage": round(percentage, 1)
        })

    return {
        "question": poll["question"],
        "results": results,
        "totalVotes": total_votes
    }