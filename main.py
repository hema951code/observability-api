import time
import uuid
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# ============================================================
# EDIT THIS ONE LINE: put your logged-in email here
# ============================================================
YOUR_EMAIL = "22f1000951@ds.study.iitm.ac.in"

START_TIME = time.time()

REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests received")

# In-memory ring buffer of the last 1000 structured log entries.
LOG_BUFFER = deque(maxlen=1000)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        REQUEST_COUNTER.inc()
        request_id = str(uuid.uuid4())

        response = await call_next(request)

        LOG_BUFFER.append({
            "level": "info",
            "ts": time.time(),
            "path": request.url.path,
            "request_id": request_id,
            "method": request.method,
            "status_code": response.status_code,
        })

        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(ObservabilityMiddleware)


@app.get("/work")
def work(n: int = 0):
    total = 0
    for i in range(n):
        total += i
    return {"email": YOUR_EMAIL, "done": n}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "uptime_s": time.time() - START_TIME}


@app.get("/logs/tail")
def logs_tail(limit: int = 10):
    entries = list(LOG_BUFFER)[-limit:] if limit > 0 else []
    return JSONResponse(content=entries)
