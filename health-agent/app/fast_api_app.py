# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://www.apache.org/licenses/LICENSE-2.0

import os
import uuid
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

import google.auth
from google.adk.cli.fast_api import get_fast_api_app
from app.app_utils.telemetry import setup_telemetry
from app.app_utils.typing import Feedback

from app.agent import app as adk_app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Initialize telemetry
setup_telemetry()

# Configure logging with a robust fallback for local running without GCP credentials
try:
    from google.cloud import logging as google_cloud_logging
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
    use_gcloud_logging = True
except Exception:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("web_server")
    use_gcloud_logging = False

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None
artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

# Initialize FastAPI using ADK wrapper to satisfy test fixtures
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=use_gcloud_logging,
)
app.title = "HealthInsight AI"
app.description = "Public Health Decision Intelligence Platform API"

# Configure local session service for custom endpoints
session_service = InMemorySessionService()

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback."""
    if use_gcloud_logging:
        logger.log_struct(feedback.model_dump(), severity="INFO")
    else:
        logger.info(f"Feedback received: {feedback.model_dump()}")
    return {"status": "success"}

# --- Custom Dashboard and Analytics Endpoints ---

@app.get("/api/chat")
async def chat_stream(query: str, session_id: str = None):
    """Streams execution events of the multi-agent system back to the client using SSE."""
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:10]}"
        
    async def event_generator():
        runner = Runner(
            app=adk_app,
            session_service=session_service
        )
        
        try:
            await session_service.create_session(app_name="app", user_id="web_user", session_id=session_id)
        except Exception:
            pass # Already exists
            
        new_msg = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        
        try:
            async for event in runner.run_async(
                user_id="web_user",
                session_id=session_id,
                new_message=new_msg,
                yield_user_message=True
            ):
                event_dict = event.model_dump(mode="json")
                yield {
                    "event": "agent_event",
                    "data": json.dumps({
                        "author": event_dict.get("author") or "system",
                        "event_id": event_dict.get("id"),
                        "content": event_dict.get("content"),
                        "output": event_dict.get("output"),
                        "actions": event_dict.get("actions"),
                        "timestamp": event_dict.get("timestamp")
                    })
                }
        except Exception as e:
            if use_gcloud_logging:
                logger.log_struct({"error": str(e)}, severity="ERROR")
            else:
                logger.exception("Error during agent execution")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
            
    return EventSourceResponse(event_generator())

@app.get("/api/session/clear")
async def clear_session(session_id: str):
    """Explicitly deletes session in-memory to prevent data retention."""
    try:
        await session_service.delete_session(app_name="app", user_id="web_user", session_id=session_id)
        return {"status": "success", "message": f"Session {session_id} successfully cleared."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/analytics")
async def get_analytics():
    """Returns community health metrics and trends for the dashboard."""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "community_health_data.csv")
    if not os.path.exists(csv_path):
        return {"error": "Community health data not found"}
        
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # 1. Total Cases
        total_cases = int(df['cases'].sum())
        
        # 2. Highest Risk Region
        region_cases = df.groupby('region')['cases'].sum()
        highest_risk_region = region_cases.idxmax()
        
        # 3. Average Vaccination Rate
        avg_vac_rate = float(df['vaccination_rate'].mean())
        
        # 4. Current Risk Level based on MoM increase
        dates = sorted(df['date'].unique())
        risk_level = "Low Risk"
        recs = []
        if len(dates) >= 2:
            latest_date = dates[-1]
            prev_date = dates[-2]
            latest_cases = int(df[df['date'] == latest_date]['cases'].sum())
            prev_cases = int(df[df['date'] == prev_date]['cases'].sum())
            
            if prev_cases > 0:
                increase_pct = (latest_cases - prev_cases) / prev_cases * 100.0
            else:
                increase_pct = 100.0 if latest_cases > 0 else 0.0
                
            if increase_pct > 25.0:
                risk_level = "High Risk"
            elif increase_pct > 0.0:
                risk_level = "Medium Risk"
            else:
                risk_level = "Low Risk"
                
        # Generate targeted recommendations based on disease MoM increases
        if len(dates) >= 2:
            latest_df = df[df['date'] == dates[-1]]
            prev_df = df[df['date'] == dates[-2]]
            for disease in df['disease'].unique():
                latest_d_cases = latest_df[latest_df['disease'] == disease]['cases'].sum()
                prev_d_cases = prev_df[prev_df['disease'] == disease]['cases'].sum()
                
                pct_chg = (latest_d_cases - prev_d_cases) / prev_d_cases * 100.0 if prev_d_cases > 0 else (100.0 if latest_d_cases > 0 else 0.0)
                
                if pct_chg > 25.0:
                    if disease.lower() == "dengue":
                        recs.append(f"Dengue cases rose by {pct_chg:.1f}%. Conduct mosquito control and eliminate standing water.")
                    elif "heat stroke" in disease.lower():
                        recs.append(f"Heat Stroke cases spiked by {pct_chg:.1f}%. Set up cooling shelters and issue hydration alerts.")
                    elif "influenza" in disease.lower():
                        recs.append(f"Influenza cases increased by {pct_chg:.1f}%. Boost community influenza vaccination drives.")
                    else:
                        recs.append(f"{disease} cases rose by {pct_chg:.1f}%. Increase public awareness campaigns.")
                elif pct_chg > 0.0:
                    recs.append(f"Promote routine prevention for {disease} due to slight upward case trend (+{pct_chg:.1f}%).")
                    
        if not recs:
            recs.append("All disease trends are currently stable or decreasing. Maintain basic hand hygiene and wellness checks.")
            
        # 5. Trend Data grouped by date and disease
        trend_groups = df.groupby(['date', 'disease'])['cases'].sum().unstack(fill_value=0)
        labels = list(trend_groups.index)
        datasets = []
        for col in trend_groups.columns:
            datasets.append({
                "label": str(col),
                "data": [int(v) for v in trend_groups[col]]
            })
            
        trend_data = {
            "labels": labels,
            "datasets": datasets
        }
        
        return {
            "total_cases": total_cases,
            "highest_risk_region": highest_risk_region,
            "average_vaccination_rate": avg_vac_rate,
            "risk_level": risk_level,
            "recommendations": recs,
            "trend_data": trend_data
        }
    except Exception as e:
        if use_gcloud_logging:
            logger.log_struct({"error": str(e)}, severity="ERROR")
        else:
            logger.error(f"Error in /api/analytics: {str(e)}")
        return {"error": str(e)}

# Serve Static UI Files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Web dashboard static files are being prepared... Please reload in a moment.</h3>"

app.mount("/static", StaticFiles(directory=static_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
