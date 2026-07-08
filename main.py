from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import time
import uuid

app = FastAPI()

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-8i4ctb3o.apps.exam.local"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

class TokenRequest(BaseModel):
    token: str

@app.post("/verify")
async def verify_token(request: TokenRequest):

    try:

        payload = jwt.decode(
            request.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud")
        }

    except Exception:

        return JSONResponse(
            status_code=401,
            content={"valid": False}
        )

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
        "email": "21f3000721@ds.study.iitm.ac.in",
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count
    }