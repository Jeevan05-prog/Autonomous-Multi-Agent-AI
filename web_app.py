from __future__ import annotations

import csv
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    abort,
)

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

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


job_lock = threading.Lock()

jobs: dict[str, dict[str, Any]] = {}

jobs_lock = threading.Lock()


AGENT_ORDER = [
    "planner",
    "researcher",
    "data_analyst",
    "insight",
    "critic",
    "report",
]


def clear_old_outputs():

    """
    Remove old charts and reports before a new research run.

    This prevents previous EV charts from appearing
    in a completely different research topic.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    old_chart_names = [
        "total_trend.png",
        "category_trends.png",
        "latest_share.png",
    ]

    for name in old_chart_names:

        path = CHART_DIR / name

        if path.exists():

            try:
                path.unlink()
            except OSError as error:
                print(f"Could not remove old chart {path}: {error}")

    old_analysis = OUTPUT_DIR / "analysis" / "data_analysis.txt"

    if old_analysis.exists():

        try:
            old_analysis.unlink()
        except OSError:
            pass

    if REPORT_PATH.exists():

        try:
            REPORT_PATH.unlink()
        except OSError:
            pass


def make_web_only_analysis(research: str) -> str:

    """
    Web-only mode does not use an old CSV dataset.

    It extracts numerical statements from current research.
    It does not create fake charts or invent statistics.
    """

    text = research or ""

    candidates = []

    for raw_line in text.splitlines():

        line = " ".join(raw_line.split()).strip(" -*\t")

        if not line:
            continue

        if line.lower().startswith(("http://", "https://")):
            continue

        if any(char.isdigit() for char in line):

            if line not in candidates:
                candidates.append(line)

    if not candidates:

        return """

WEB RESEARCH ONLY — DATA ANALYSIS

No CSV dataset was uploaded.

The Data Analyst reviewed the collected research,
but no suitable numerical evidence could be extracted.

No numerical values or graphs have been invented.

For statistical analysis, upload a relevant CSV dataset.

"""

    evidence = candidates[:15]

    bullets = "\n".join(
        f"- {item}" for item in evidence
    )

    return f"""

WEB RESEARCH ONLY — DATA ANALYSIS

No CSV dataset was uploaded.

The Data Analyst reviewed the numerical statements
collected by the Research Agent.

The following statements were found:

{bullets}


IMPORTANT LIMITATIONS

These are figures or numerical statements reported
in the collected research.

They are not calculations from a complete dataset.

Different sources may use different definitions,
time periods and measurement methods.

No unrelated dataset has been used.

No dataset-based graphs have been generated.

"""


def web_data_analyst(state: AgentState):

    """
    Use uploaded CSV only when the user uploads one.

    Otherwise, perform web-only evidence extraction.
    """

    dataset_path = str(
        state.get("dataset_path", "") or ""
    ).strip()

    if dataset_path:

        print("\nData Analyst: analysing uploaded CSV.")

        return data_analyst_agent(state)

    updated = dict(state)

    updated["analysis"] = make_web_only_analysis(
        str(state.get("research", ""))
    )

    analysis_dir = OUTPUT_DIR / "analysis"

    analysis_dir.mkdir(parents=True, exist_ok=True)

    (analysis_dir / "data_analysis.txt").write_text(
        updated["analysis"],
        encoding="utf-8",
    )

    print("\nData Analyst: web-only evidence extraction completed.")

    return updated


def create_website_workflow():

    builder = StateGraph(AgentState)

    def run_researcher(state):

        state["research_round"] = (
            state.get("research_round", 0) + 1
        )

        print(
            f"\nResearch Attempt: {state['research_round']}"
        )

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
        {
            "research": "researcher",
            "report": "report",
        },
    )

    builder.add_edge("report", END)

    return builder.compile()


def safe_job_update(job_id: str, **kwargs):

    with jobs_lock:

        if job_id in jobs:

            jobs[job_id].update(kwargs)


def next_agent_after(node_name, state):

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

            return (
                "researcher"
                if route == "research"
                else "report"
            )

        except Exception:

            return "report"

    return None


def run_job(job_id, topic, dataset_path):

    statuses = {
        name: "waiting"
        for name in AGENT_ORDER
    }

    state = {

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
            started_at=datetime.now().isoformat(
                timespec="seconds"
            ),
        )

        workflow = create_website_workflow()

        for update in workflow.stream(
            state,
            stream_mode="updates",
        ):

            for node_name, node_update in update.items():

                if isinstance(node_update, dict):

                    state.update(node_update)

                if node_name in statuses:

                    statuses[node_name] = "completed"

                next_name = next_agent_after(
                    node_name,
                    state,
                )

                if (
                    next_name
                    and statuses.get(next_name) != "completed"
                ):

                    statuses[next_name] = "running"

                safe_job_update(
                    job_id,
                    current_agent=next_name or node_name,
                    agent_status=dict(statuses),
                    state=dict(state),
                    research_round=state.get(
                        "research_round", 0
                    ),
                )

        report_text = ""

        if REPORT_PATH.exists():

            report_text = REPORT_PATH.read_text(
                encoding="utf-8",
                errors="replace",
            )

        safe_job_update(
            job_id,
            status="completed",
            current_agent="completed",
            agent_status={
                name: "completed"
                for name in AGENT_ORDER
            },
            state=dict(state),
            report=report_text,
            finished_at=datetime.now().isoformat(
                timespec="seconds"
            ),
            error=None,
        )

        print("\nResearch workflow completed successfully.")

    except Exception as exc:

        print("\nWORKFLOW ERROR:", exc)

        safe_job_update(
            job_id,
            status="failed",
            current_agent="failed",
            state=dict(state),
            error=f"{type(exc).__name__}: {exc}",
            agent_status=dict(statuses),
            finished_at=datetime.now().isoformat(
                timespec="seconds"
            ),
        )

    finally:

        job_lock.release()


@app.get("/")
def home():

    return render_template("index.html")


@app.get("/api/health")
def health():

    return jsonify({
        "ok": True,
        "app": "ResearchFlow AI",
    })


@app.post("/api/research")
def start_research():

    topic = (
        request.form.get("topic") or ""
    ).strip()

    if not topic:

        return jsonify({
            "error": "Please enter a research topic."
        }), 400

    dataset_path = ""

    uploaded = request.files.get("dataset")

    if uploaded and uploaded.filename:

        filename = secure_filename(
            uploaded.filename
        )

        if not filename.lower().endswith(".csv"):

            return jsonify({
                "error": "Please upload a CSV file only."
            }), 400

    if not job_lock.acquire(blocking=False):

        return jsonify({
            "error": (
                "A research workflow is already running. "
                "Please wait for it to finish."
            )
        }), 409

    try:

        if uploaded and uploaded.filename:

            filename = secure_filename(
                uploaded.filename
            )

            unique_name = (
                f"{uuid.uuid4().hex[:10]}_{filename}"
            )

            saved_path = UPLOAD_DIR / unique_name

            uploaded.save(saved_path)

            try:

                with saved_path.open(
                    "r",
                    encoding="utf-8-sig",
                    newline="",
                ) as handle:

                    csv.reader(handle).__next__()

                dataset_path = str(saved_path)

            except Exception:

                saved_path.unlink(missing_ok=True)

                job_lock.release()

                return jsonify({
                    "error": (
                        "The uploaded file could not "
                        "be read as a CSV."
                    )
                }), 400

        # Remove previous charts and reports
        # before starting a fresh research run.

        clear_old_outputs()

        job_id = uuid.uuid4().hex

        mode = (
            "Research + Data Analysis"
            if dataset_path
            else "Web Research Only"
        )

        with jobs_lock:

            jobs[job_id] = {

                "job_id": job_id,

                "status": "queued",

                "topic": topic,

                "mode": mode,

                "current_agent": "queued",

                "agent_status": {
                    name: "waiting"
                    for name in AGENT_ORDER
                },

                "state": {},

                "report": "",

                "error": None,

                "created_at": datetime.now().isoformat(
                    timespec="seconds"
                ),

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

            "mode": mode,

        }), 202

    except Exception as exc:

        if job_lock.locked():

            job_lock.release()

        return jsonify({
            "error": str(exc)
        }), 500


@app.get("/api/status/<job_id>")
def job_status(job_id):

    with jobs_lock:

        job = jobs.get(job_id)

        if not job:

            return jsonify({
                "error": "Research job not found."
            }), 404

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

    return jsonify({
        "report": report
    })


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

    return send_from_directory(
        OUTPUT_DIR,
        filename,
    )


@app.errorhandler(413)
def file_too_large(_error):

    return jsonify({
        "error": (
            "The CSV file is too large. "
            "Maximum size is 20 MB."
        )
    }), 413


if __name__ == "__main__":

    print("\nResearchFlow AI website starting...")

    print("Open http://127.0.0.1:5000 in your browser.\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True,
    )