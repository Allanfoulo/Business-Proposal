import base64
import uuid
from typing import Dict, Any, List, Tuple

from flask import Flask, render_template, request, Response, redirect, url_for

from llm_provider import call_llm, stream_llm
from llm_parallel_core import generate_all_sections_parallel_core
from export_utils import build_pdf, build_docx


app = Flask(__name__, template_folder="templates")

# Simple in-memory job store for streaming sessions
JOBS: Dict[str, Dict[str, Any]] = {}


def _mk_prompt(title: str, body_instructions: str, data: Dict[str, Any]) -> str:
    company = data.get("company_name") or "Your Company"
    industry = data.get("industry") or data.get("market") or "General"
    mission = data.get("mission") or ""
    vision = data.get("vision") or ""
    products = data.get("products") or ""
    market = data.get("market") or ""
    financials = data.get("financials") or ""
    team = data.get("team") or ""
    goals = data.get("goals") or ""
    strategies = data.get("strategies") or ""

    return (
        f"Write the {title} for a business proposal.\n"
        f"Company: {company}\nIndustry: {industry}\n"
        f"Mission: {mission}\nVision: {vision}\nProducts: {products}\n"
        f"Market: {market}\nFinancials: {financials}\nTeam: {team}\n"
        f"Goals: {goals}\nStrategies: {strategies}\n\n"
        f"{body_instructions}\n"
        f"Use clear markdown with headings and bullet points."
    )


SECTION_GENERATORS: List[Tuple[str, Any]] = [
    (
        "executive_summary",
        lambda d: _mk_prompt(
            "Executive Summary",
            "Summarize the proposal with key value proposition, market opportunity, product offering, go-to-market, and financial highlights.",
            d,
        ),
    ),
    (
        "company_overview",
        lambda d: _mk_prompt(
            "Company Overview",
            "Describe company history, mission, vision, leadership, and core competencies.",
            d,
        ),
    ),
    (
        "products_services",
        lambda d: _mk_prompt(
            "Products and Services",
            "Outline the offerings, differentiators, pricing approach, and roadmap.",
            d,
        ),
    ),
    (
        "market_analysis",
        lambda d: _mk_prompt(
            "Market Analysis",
            "Explain target segments, TAM/SAM/SOM if relevant, competitors, and trends.",
            d,
        ),
    ),
    (
        "go_to_market",
        lambda d: _mk_prompt(
            "Go-To-Market Strategy",
            "Detail acquisition channels, positioning, messaging, sales motion, partnerships.",
            d,
        ),
    ),
    (
        "operations_plan",
        lambda d: _mk_prompt(
            "Operations Plan",
            "Cover delivery model, fulfillment, support, KPIs, and operational risks.",
            d,
        ),
    ),
    (
        "financial_plan",
        lambda d: _mk_prompt(
            "Financial Plan",
            "Include revenue model, cost structure, unit economics, and forecast assumptions.",
            d,
        ),
    ),
    (
        "team_organization",
        lambda d: _mk_prompt(
            "Team and Organization",
            "Highlight key roles, hiring plan, org chart, advisors.",
            d,
        ),
    ),
    (
        "milestones_roadmap",
        lambda d: _mk_prompt(
            "Milestones and Roadmap",
            "Present recent achievements and upcoming timeline with measurable deliverables.",
            d,
        ),
    ),
    (
        "risk_mitigation",
        lambda d: _mk_prompt(
            "Risk and Mitigation",
            "Identify top risks and practical mitigation strategies.",
            d,
        ),
    ),
]

SECTION_TO_HEADER: Dict[str, str] = {
    "executive_summary": "Executive Summary",
    "company_overview": "Company Overview",
    "products_services": "Products and Services",
    "market_analysis": "Market Analysis",
    "go_to_market": "Go-To-Market Strategy",
    "operations_plan": "Operations Plan",
    "financial_plan": "Financial Plan",
    "team_organization": "Team and Organization",
    "milestones_roadmap": "Milestones and Roadmap",
    "risk_mitigation": "Risk and Mitigation",
}


@app.route("/")
def index():
    sections = [key for key, _ in SECTION_GENERATORS]
    headers = {k: SECTION_TO_HEADER[k] for k in sections}
    return render_template("index.html", sections=sections, headers=headers)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/generate", methods=["POST"])
def generate():
    form = request.form

    # Capture provider settings
    provider = form.get("provider", "ollama")
    model = form.get("model") or None
    parallel_mode = form.get("parallel_mode") == "on"
    max_workers = int(form.get("max_workers", "5") or 5)
    live_stream = form.get("live_stream") == "on"

    # Collect data fields
    data: Dict[str, Any] = {
        "company_name": form.get("company_name", ""),
        "industry": form.get("industry", ""),
        "mission": form.get("mission", ""),
        "vision": form.get("vision", ""),
        "products": form.get("products", ""),
        "market": form.get("market", ""),
        "financials": form.get("financials", ""),
        "team": form.get("team", ""),
        "goals": form.get("goals", ""),
        "strategies": form.get("strategies", ""),
    }

    # Per-section toggles: skip | normal | priority
    selected_priority: List[Tuple[str, Any]] = []
    selected_normal: List[Tuple[str, Any]] = []
    for key, gen in SECTION_GENERATORS:
        choice = form.get(f"section_choice_{key}", "normal")
        if choice == "skip":
            continue
        elif choice == "priority":
            selected_priority.append((key, gen))
        else:
            selected_normal.append((key, gen))

    ordered_sections: List[Tuple[str, Any]] = selected_priority + selected_normal
    section_order = [k for k, _ in ordered_sections]

    if live_stream:
        job_id = str(uuid.uuid4())
        JOBS[job_id] = {
            "data": data,
            "provider": provider,
            "model": model,
            "selected": section_order,
            "results": {},
        }
        return render_template(
            "results.html",
            section_order=section_order,
            headers={k: SECTION_TO_HEADER[k] for k in section_order},
            results={},
            streaming_enabled=True,
            job_id=job_id,
            provider=provider,
            model=model or "",
            pdf_b64=None,
            docx_b64=None,
        )

    # Non-streaming: parallel generation with retry/backoff built-in
    results_map = generate_all_sections_parallel_core(
        data=data,
        call_llm_func=lambda prompt: call_llm(prompt, provider=provider, model=model),
        section_generators=ordered_sections,
        max_workers=max_workers if parallel_mode else 1,
        on_progress=None,
        max_attempts=3,
        initial_backoff=1.0,
    )

    # Build exports
    headers_map = {k: SECTION_TO_HEADER[k] for k in section_order}
    pdf_bytes = build_pdf(results_map, section_order, headers_map)
    docx_bytes = build_docx(results_map, section_order, headers_map)
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
    docx_b64 = base64.b64encode(docx_bytes).decode("ascii")

    return render_template(
        "results.html",
        section_order=section_order,
        headers=headers_map,
        results=results_map,
        streaming_enabled=False,
        job_id="",
        provider=provider,
        model=model or "",
        pdf_b64=pdf_b64,
        docx_b64=docx_b64,
    )


@app.route("/stream/<key>")
def stream_section(key: str):
    job_id = request.args.get("job_id")
    provider = request.args.get("provider", "ollama")
    model = request.args.get("model") or None

    job = JOBS.get(job_id)
    if not job:
        return Response("event: error\ndata: invalid job\n\n", mimetype="text/event-stream")
    if key not in job.get("selected", []):
        return Response("event: error\ndata: section not selected\n\n", mimetype="text/event-stream")

    # Find generator
    gen_map = {k: g for k, g in SECTION_GENERATORS}
    generator = gen_map.get(key)
    if generator is None:
        return Response("event: error\ndata: unknown section\n\n", mimetype="text/event-stream")

    prompt = generator(job["data"])

    def _event_stream():
        try:
            buf: List[str] = []
            for chunk in stream_llm(prompt, provider=provider, model=model):
                if not chunk:
                    continue
                buf.append(chunk)
                job["results"][key] = "".join(buf)
                yield f"event: chunk\ndata: {chunk}\n\n"
            yield "event: done\ndata: done\n\n"
        except Exception as e:
            yield f"event: error\ndata: {e}\n\n"

    resp = Response(_event_stream(), mimetype="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


@app.route("/build/<job_id>", methods=["POST"]) 
def build_exports(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return redirect(url_for("index"))

    section_order = job.get("selected", [])
    headers_map = {k: SECTION_TO_HEADER[k] for k in section_order}
    pdf_bytes = build_pdf(job["results"], section_order, headers_map)
    docx_bytes = build_docx(job["results"], section_order, headers_map)
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")
    docx_b64 = base64.b64encode(docx_bytes).decode("ascii")

    return render_template(
        "results.html",
        section_order=section_order,
        headers=headers_map,
        results=job["results"],
        streaming_enabled=False,
        job_id=job_id,
        provider=job.get("provider", ""),
        model=job.get("model", "") or "",
        pdf_b64=pdf_b64,
        docx_b64=docx_b64,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)