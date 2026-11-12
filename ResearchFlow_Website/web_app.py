from __future__ import annotations

import csv
import json
import re
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_from_directory, abort
from werkzeug.utils import secure_filename

from langgraph.graph import StateGraph, START, END

from models.state import AgentState
from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.data_analyst import data_analyst_agent
from agents.insight import insight_agent
from agents.critic import critic_agent, route_after_critique
from agents.report import report_agent


ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "datasets" / "uploads"
OUTPUT_DIR = ROOT / "outputs"
REPORT_PATH = OUTPUT_DIR / "final_report.md"
CHART_DIR = OUTPUT_DIR / "charts"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(ROOT / "website" / "templates"),
    static_folder=str(ROOT / "website" / "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

# The existing agents write to shared output paths. One workflow at a time
# prevents two website runs from overwriting each other's reports/charts.
job_lock = threading.Lock()
jobs: dict[str, dict[str, Any]] = {}
jobs_lock = threading.Lock()

AGENT_ORDER = ["planner", "researcher", "data_analyst", "insight", "critic", "report"]
AGENT_LABELS = {
    "planner": "Planner Agent",
    "researcher": "Research Agent",
    "data_analyst": "Data Analyst Agent",
    "insight": "Insight Agent",
    "critic": "Critic Agent",
    "report": "Report Agent",
}


def make_web_only_analysis(research: str) -> str:
    """
    When no CSV is uploaded, the Data Analyst node extracts numerical evidence
    explicitly present in the research text. It does not invent missing values
    or claim that snippets form a complete dataset.
    """
    text = research or ""
    candidates = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip(" -*\t")
        if not line:
            continue
        if re.search(r"\d", line) and not line.lower().startswith(("http://", "https://")):
            if line not in candidates:
                candidates.append(line)

    if not candidates:
        return (
            "WEB-ONLY DATA ANALYSIS\n\n"
            "No CSV dataset was uploaded. The Data Analyst checked the collected "
            "research text but could not identify enough clearly stated numerical "
            "evidence to summarize. No numerical values have been invented.\n\n"
            "For deeper quantitative analysis, upload a structured CSV dataset."
        )

    evidence = candidates[:12]
    bullets = "\n".join(f"- {item}" for item in evidence)
    return (
        "WEB-ONLY DATA ANALYSIS\n\n"
        "No CSV dataset was uploaded. The Data Analyst reviewed the numerical "
        "statements present in the web research and extracted the evidence below. "
        "These are source-reported figures, not calculations from a complete "
        "dataset. Different sources may use different dates, definitions, or "
        "measurement methods, so compare them carefully.\n\n"
        f"NUMERICAL EVIDENCE FOUND ({len(evidence)} items shown)\n{bullets}\n\n"
        "LIMITATION\n"
        "This is evidence extraction, not a statistical analysis of raw data. "
        "Upload a CSV to generate calculated totals, growth rates, comparisons, "
        "and charts."
    )


def web_data_analyst(state: AgentState):
    """Use the existing CSV analyst when a file is supplied; otherwise analyse
    numerical evidence collected by the Research Agent."""
    dataset_path = str(state.get("dataset_path", "") or "").strip()

    if dataset_path:
        return data_analyst_agent(state)

    updated = dict(state)
    updated["analysis"] = make_web_only_analysis(str(state.get("research", "")))

    analysis_dir = OUTPUT_DIR / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "data_analysis.txt").write_text(
        updated["analysis"], encoding="utf-8"
    )
    print("\nData Analyst: completed web-only numerical evidence review.")
    return updated


def create_website_workflow():
    """Build the same six-agent workflow, using a web-only analyst when no CSV
    is provided. The original CLI workflow remains untouched."""
    builder = StateGraph(AgentState)

    def run_researcher(state):
        state["research_round"] = state.get("research_round", 0) + 1
        print(f"\nResearch Attempt: {state['research_round']}")
        return researcher_agent(state)

    builder.add_node("planner", planner_agent)
    builder.add_node("researcher", run_researcher)
    builder.add_node("data_analyst", web_data_analyst)
    builder.add_node("insight", insight_agent)
    builder.add_node("critic", critic_agent)
    builder.add_node("report", report_agent)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "data_analyst")
    builder.add_edge("data_analyst", "insight")
    builder.add_edge("insight", "critic")
    builder.add_conditional_edges(
        "critic",
        route_after_critique,
        {"research": "researcher", "report": "report"},
    )
    builder.add_edge("report", END)
    return builder.compile()


def safe_job_update(job_id: str, **kwargs):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(kwargs)


def next_agent_after(node_name: str, state: dict[str, Any]) -> str | None:
    if node_name == "planner":
        return "researcher"
    if node_name == "researcher":
        return "data_analyst"
    if node_name == "data_analyst":
        return "insight"
    if node_name == "insight":
        return "critic"
    if node_name == "critic":
        try:
            route = route_after_critique(state)
            return "researcher" if route == "research" else "report"
        except Exception:
            return "report"
    return None


def run_job(job_id: str, topic: str, dataset_path: str):
    statuses = {name: "waiting" for name in AGENT_ORDER}
    state: dict[str, Any] = {
        "user_request": topic,
        "plan": [],
        "research": "",
        "dataset_path": dataset_path,
        "analysis": "",
        "insights": "",
        "critique": "",
        "final_report": "",
        "research_round": 0,
    }

    try:
        safe_job_update(
            job_id,
            status="running",
            current_agent="planner",
            agent_status=statuses,
            started_at=datetime.now().isoformat(timespec="seconds"),
        )

        workflow = create_website_workflow()

        for update in workflow.stream(state, stream_mode="updates"):
            for node_name, node_update in update.items():
                if isinstance(node_update, dict):
                    state.update(node_update)

                if node_name in statuses:
                    statuses[node_name] = "completed"

                next_name = next_agent_after(node_name, state)
                if next_name and statuses.get(next_name) != "completed":
                    statuses[next_name] = "running"

                safe_job_update(
                    job_id,
                    current_agent=next_name or node_name,
                    agent_status=dict(statuses),
                    state=dict(state),
                    research_round=state.get("research_round", 0),
                )

        report_text = ""
        if REPORT_PATH.exists():
            report_text = REPORT_PATH.read_text(encoding="utf-8", errors="replace")

        safe_job_update(
            job_id,
            status="completed",
            current_agent="completed",
            agent_status={name: "completed" for name in AGENT_ORDER},
            state=dict(state),
            report=report_text,
            finished_at=datetime.now().isoformat(timespec="seconds"),
            error=None,
        )

    except Exception as exc:
        safe_job_update(
            job_id,
            status="failed",
            current_agent="failed",
            state=dict(state),
            error=f"{type(exc).__name__}: {exc}",
            agent_status=dict(statuses),
            finished_at=datetime.now().isoformat(timespec="seconds"),
        )
    finally:
        job_lock.release()


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "app": "ResearchFlow AI"})


@app.post("/api/research")
def start_research():
    topic = (request.form.get("topic") or "").strip()
    if not topic:
        return jsonify({"error": "Please enter a research topic."}), 400

    if not job_lock.acquire(blocking=False):
        return jsonify({
            "error": "A research workflow is already running. Please wait for it to finish."
        }), 409

    dataset_path = ""
    uploaded = request.files.get("dataset")
    if uploaded and uploaded.filename:
        filename = secure_filename(uploaded.filename)
        if not filename.lower().endswith(".csv"):
            job_lock.release()
            return jsonify({"error": "Please upload a CSV file only."}), 400

        unique_name = f"{uuid.uuid4().hex[:10]}_{filename}"
        saved_path = UPLOAD_DIR / unique_name
        try:
            uploaded.save(saved_path)
            # Validate that it is at least readable as a CSV.
            with saved_path.open("r", encoding="utf-8-sig", newline="") as handle:
                csv.reader(handle).__next__()
            dataset_path = str(saved_path)
        except Exception:
            try:
                saved_path.unlink(missing_ok=True)
            except Exception:
                pass
            job_lock.release()
            return jsonify({"error": "The uploaded file could not be read as a CSV."}), 400

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "topic": topic,
            "mode": "Research + Data Analysis" if dataset_path else "Web Research Only",
            "current_agent": "queued",
            "agent_status": {name: "waiting" for name in AGENT_ORDER},
            "state": {},
            "report": "",
            "error": None,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

    thread = threading.Thread(
        target=run_job,
        args=(job_id, topic, dataset_path),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "job_id": job_id,
        "message": "Research workflow started.",
        "mode": jobs[job_id]["mode"],
    }), 202


@app.get("/api/status/<job_id>")
def job_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify({"error": "Research job not found."}), 404
        # Return a copy so Flask can safely serialize it.
        result = dict(job)

    state = result.get("state") or {}
    result["summary"] = {
        "research": state.get("research", ""),
        "analysis": state.get("analysis", ""),
        "insights": state.get("insights", ""),
        "critique": state.get("critique", ""),
        "plan": state.get("plan", []),
    }
    result.pop("state", None)
    return jsonify(result)


@app.get("/api/report/<job_id>")
def get_report(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        report = job.get("report", "")
    if not report and REPORT_PATH.exists():
        report = REPORT_PATH.read_text(encoding="utf-8", errors="replace")
    return jsonify({"report": report})


@app.get("/api/report/<job_id>/download")
def download_report(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
    if not REPORT_PATH.exists():
        abort(404)
    return send_from_directory(
        OUTPUT_DIR,
        REPORT_PATH.name,
        as_attachment=True,
        download_name="research_report.md",
    )


@app.get("/outputs/<path:filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "The CSV file is too large. Maximum size is 20 MB."}), 413


if __name__ == "__main__":
    print("\nResearchFlow AI website starting...")
    print("Open http://127.0.0.1:5000 in your browser.\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
