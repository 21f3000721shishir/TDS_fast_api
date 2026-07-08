from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-mtzp3i.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_headers(request, call_next):

    start = time.time()

    response = await call_next(request)

    process_time = time.time() - start

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/")
def home():
    return {"status": "running"}


@app.get("/stats")
def stats(values: str = Query(...)):

    numbers = [int(x) for x in values.split(",")]

    count = len(numbers)
    total = sum(numbers)

    return {
        "email": "your_email@example.com",
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count
    }