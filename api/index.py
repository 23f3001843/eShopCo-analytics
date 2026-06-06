from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json, os, numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
with open(DATA_PATH) as f:
    TELEMETRY = json.load(f)

class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/api/analytics")
def analytics(req: AnalyticsRequest):
    result = {}
    for region in req.regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 4),
            "p95_latency": round(float(np.percentile(latencies, 95)), 4),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": int(sum(1 for l in latencies if l > req.threshold_ms))
        }
    return result