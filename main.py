from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


def check_rate_limit(client_id):

    now = time.time()

    requests = client_requests.get(
        client_id,
        []
    )

    requests = [
        t for t in requests
        if now - t < WINDOW
    ]

    if len(requests) >= RATE_LIMIT:

        retry_after = int(
            WINDOW - (now - requests[0])
        ) + 1

        return JSONResponse(
            status_code=429,
            content={
                "detail": "rate limit exceeded"
            },
            headers={
                "Retry-After": str(retry_after)
            }
        )

    requests.append(now)

    client_requests[client_id] = requests

    return None


@app.post("/orders", status_code=201)
def create_order(
    request: Request,
    idempotency_key: str = Header(
        alias="Idempotency-Key"
    )
):

    client_id = request.headers.get(
        "X-Client-Id",
        "anonymous"
    )

    limited = check_rate_limit(client_id)

    if limited:
        return limited

    if idempotency_key in idempotency_store:
        return idempotency_store[
            idempotency_key
        ]

    order = {
        "id": str(uuid.uuid4())
    }

    idempotency_store[
        idempotency_key
    ] = order

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

    limited = check_rate_limit(client_id)

    if limited:
        return limited

    start = 0

    if cursor:
        start = int(cursor)

    items = ORDERS[
        start:start + limit
    ]

    next_cursor = None

    if start + limit < len(ORDERS):
        next_cursor = str(
            start + limit
        )

    return {
        "items": items,
        "next_cursor": next_cursor
    }