
from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TOTAL_ORDERS = 52
RATE_LIMIT = 20
WINDOW = 10

ORDERS = [
    {"id": i, "name": f"Order-{i}"}
    for i in range(1, TOTAL_ORDERS + 1)
]

idempotency_store = {}
client_requests = {}


def check_rate_limit(client_id: str):
    now = time.time()

    timestamps = client_requests.get(client_id, [])

    # Keep only requests within the last 10 seconds
    timestamps = [
        t for t in timestamps
        if now - t < WINDOW
    ]

    if len(timestamps) >= RATE_LIMIT:
        retry_after = max(
            1,
            int(WINDOW - (now - timestamps[0])) + 1
        )

        raise HTTPException(
            status_code=429,
            detail="rate limit exceeded",
            headers={
                "Retry-After": str(retry_after)
            }
        )

    timestamps.append(now)
    client_requests[client_id] = timestamps


@app.post("/orders", status_code=201)
def create_order(
    request: Request,
    idempotency_key: str = Header(alias="Idempotency-Key")
):
    client_id = request.headers.get(
        "X-Client-Id",
        "anonymous"
    )

    check_rate_limit(client_id)

    if idempotency_key in idempotency_store:
        return idempotency_store[idempotency_key]

    order = {
        "id": str(uuid.uuid4())
    }

    idempotency_store[idempotency_key] = order

    return order


@app.get("/orders")
def list_orders(
    request: Request,
    limit: int = 10,
    cursor: str | None = None
):
    client_id = request.headers.get(
        "X-Client-Id",
        "anonymous"
    )

    check_rate_limit(client_id)

    start = int(cursor) if cursor else 0

    items = ORDERS[start:start + limit]

    next_cursor = None
    if start + limit < len(ORDERS):
        next_cursor = str(start + limit)

    return {
        "items": items,
        "next_cursor": next_cursor
    }


@app.get("/")
def home():
    return {"status": "running"}

