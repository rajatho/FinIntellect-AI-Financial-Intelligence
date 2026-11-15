import os
import sys
import subprocess

# Auto-re-execute using the virtual environment python interpreter if needed
venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python):
    current_python = os.path.normpath(sys.executable).lower()
    target_python = os.path.normpath(venv_python).lower()
    if current_python != target_python:
        sys.exit(subprocess.call([venv_python] + sys.argv))

import json
from flask import Flask, render_template, request, jsonify, send_file, Response, session
from flask_cors import CORS
from modules.pipeline_orchestrator import PipelineOrchestrator
from modules.document_extractor import DocumentExtractor
from modules.user_manager import UserManager

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "finintellect-production-secret-key-2025")
CORS(app)

orchestrator = PipelineOrchestrator()
extractor = DocumentExtractor()
user_manager = UserManager()

def get_current_user():
    """Extract authenticated user from Authorization header or session."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif "user_token" in session:
        token = session["user_token"]
    elif request.args.get("token"):
        token = request.args.get("token")
    
    if token:
        return user_manager.get_user_from_token(token), token
    return None, None

# ----------------- AUTHENTICATION ROUTES ----------------- #

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    company = data.get("company", "").strip()
    role = data.get("role", "Financial Analyst").strip()

    result = user_manager.register(name, email, password, company, role)
    if result["success"]:
        session["user_token"] = result["token"]
        return jsonify(result), 201
    return jsonify(result), 400

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    result = user_manager.login(email, password)
    if result["success"]:
        session["user_token"] = result["token"]
        return jsonify(result), 200
    return jsonify(result), 401

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    _, token = get_current_user()
    if token:
        user_manager.logout(token)
    session.pop("user_token", None)
    return jsonify({"success": True, "message": "Successfully logged out."})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user, token = get_current_user()
    if user:
        return jsonify({"success": True, "user": user, "token": token})
    return jsonify({"success": True, "user": None})

@app.route("/api/auth/guest-login", methods=["POST"])
def auth_guest_login():
    """Instant login as demo Lead Financial Analyst."""
    result = user_manager.login("analyst@finintellect.com", "Analyst@2025")
    if result["success"]:
        session["user_token"] = result["token"]
        return jsonify(result), 200
    return jsonify(result), 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/samples", methods=["GET"])
def get_samples():
    """List available preloaded corporate reports."""
    samples = extractor.list_available_samples()
    return jsonify({"success": True, "samples": samples})

@app.route("/api/reports", methods=["GET"])
def get_all_reports():
    """List all analyzed reports in history."""
    user, _ = get_current_user()
    user_reports = user.get("reports", []) if user else []
    reports_list = []
    for rid, rdata in orchestrator.store.items():
        v_count = len(rdata.get("versions", []))
        active_ver = rdata.get("active_version", 1)
        active_entry = next((v for v in rdata.get("versions", []) if v["version_num"] == active_ver), None)
        reports_list.append({
            "report_id": rid,
            "company": rdata.get("company"),
            "reporting_period": rdata.get("reporting_period"),
            "version_count": v_count,
            "active_version": active_ver,
            "active_label": active_entry.get("version_label") if active_entry else f"v{active_ver}",
            "risk_class": rdata.get("verified_object", {}).get("risk_prediction", {}).get("class"),
            "revenue": rdata.get("verified_object", {}).get("financial_metrics", {}).get("revenue", {}).get("formatted_current"),
            "last_updated": rdata.get("last_updated"),
            "is_user_report": (rid in user_reports) if user else True
        })
    return jsonify({"success": True, "reports": reports_list, "user": user})

@app.route("/api/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    """Retrieve full verified report, active summary, and version history."""
    report = orchestrator.get_report(report_id)
    if not report:
        return jsonify({"success": False, "error": "Report not found"}), 404
    return jsonify({"success": True, "data": report})

@app.route("/api/analyze", methods=["POST"])
def analyze_report():
    """
    Run full end-to-end pipeline:
    Document Extraction -> Data Extraction -> Validation ->
    Ratios -> Trends -> Anomalies -> ML Risk -> NLP ->
    Verified Analysis Object -> Gemini 3.5 Flash-Lite / Fallback ->
    Accuracy Audit -> PDF Ready.
    """
    payload = request.get_json() or {}
    company_name = (payload.get("company_name") or "").strip()
    sample_id = payload.get("sample_id")
    length = payload.get("length", "Standard")
    tone = payload.get("tone", "Professional")
    industry = payload.get("industry", "Technology & Software")
    reporting_period = payload.get("reporting_period", "FY2025")
    currency = payload.get("currency", "$")
    custom_metrics = payload.get("custom_metrics")
    custom_api_key = payload.get("api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if company_name:
        doc_data = extractor.create_company_report(
            company_name=company_name,
            reporting_period=reporting_period,
            industry=industry,
            currency=currency,
            custom_metrics=custom_metrics
        )
    elif sample_id:
        doc_data = extractor.get_sample_by_id(sample_id)
        if not doc_data:
            return jsonify({"success": False, "error": f"Sample '{sample_id}' not found"}), 400
    elif "document_data" in payload:
        doc_data = payload["document_data"]
    else:
        # Default to techcorp_fy25
        doc_data = extractor.get_sample_by_id("techcorp_fy25")

    try:
        result = orchestrator.run_full_pipeline(
            document_data=doc_data,
            length=length,
            tone=tone,
            custom_api_key=custom_api_key
        )
        user, _ = get_current_user()
        if user and "report_id" in result:
            user_manager.add_user_report(user["id"], result["report_id"])
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/regenerate", methods=["POST"])
def regenerate_summary():
    """
    Regenerates summary ONLY from existing verified analysis object.
    Does not re-run financial calculations.
    Appends new version to version history.
    """
    payload = request.get_json() or {}
    report_id = payload.get("report_id")
    length = payload.get("length", "Standard")
    tone = payload.get("tone", "Professional")
    custom_api_key = payload.get("api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not report_id:
        return jsonify({"success": False, "error": "report_id is required"}), 400

    try:
        result = orchestrator.regenerate_summary(
            report_id=report_id,
            length=length,
            tone=tone,
            custom_api_key=custom_api_key
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/version/restore", methods=["POST"])
def restore_version():
    """Restores an older summary version to active status."""
    payload = request.get_json() or {}
    report_id = payload.get("report_id")
    version_num = payload.get("version_num")

    if not report_id or version_num is None:
        return jsonify({"success": False, "error": "report_id and version_num required"}), 400

    try:
        result = orchestrator.restore_version(report_id, int(version_num))
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/<report_id>/pdf", methods=["GET"])
def export_pdf(report_id):
    """Generates and downloads the professional 13-section PDF report."""
    try:
        pdf_path = orchestrator.generate_pdf_for_report(report_id)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path),
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/<report_id>/export-json", methods=["GET"])
def export_json(report_id):
    """Exports full verified object and summary data as JSON."""
    report = orchestrator.get_report(report_id)
    if not report:
        return jsonify({"success": False, "error": "Report not found"}), 404

    json_str = json.dumps(report, indent=2)
    return Response(
        json_str,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={report_id}_verified_analysis.json"}
    )

@app.route("/api/reports/<report_id>/download-summary", methods=["GET"])
def download_summary(report_id):
    """Downloads active summary as a formatted Markdown text file."""
    report = orchestrator.get_report(report_id)
    if not report:
        return jsonify({"success": False, "error": "Report not found"}), 404

    active = report["active_version"]
    content = active.get("full_markdown", "")
    header = (
        f"# AI FINANCIAL SUMMARY\n"
        f"**Company:** {report['company']}\n"
        f"**Reporting Period:** {report['reporting_period']}\n"
        f"**Version:** {active.get('version_label', 'v1')}\n"
        f"**Generated Using:** {active.get('source', 'Gemini 3.5 Flash-Lite')}\n"
        f"**Validation Status:** {active.get('validation', {}).get('score', 'Verified')}\n\n---\n\n"
    )
    full_text = header + content
    return Response(
        full_text,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment;filename={report_id}_{active.get('version_label', 'v1')}_summary.md"}
    )

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Upload custom financial JSON report file."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Empty filename"}), 400

    try:
        content = file.read().decode('utf-8')
        doc_data = json.loads(content)
        result = orchestrator.run_full_pipeline(document_data=doc_data)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to parse report: {str(e)}"}), 400

@app.route("/api/status", methods=["GET"])
def status():
    """System health check and configuration status."""
    has_gemini_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or getattr(orchestrator.gemini_engine, "api_key", None))
    return jsonify({
        "status": "ONLINE",
        "has_gemini_key": has_gemini_key,
        "default_model": "gemini-3.5-flash-lite",
        "fallback_engine": "Python Deterministic Template",
        "total_reports": len(orchestrator.store)
    })

if __name__ == "__main__":
    import sys
    port = int(os.environ.get("PORT", 5001))
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    print(f"Starting FinIntellect server on http://127.0.0.1:{port}")
    try:
        app.run(host="127.0.0.1", port=port, debug=True)
    except OSError as e:
        if getattr(e, "winerror", None) == 10048 or "Address already in use" in str(e):
            print(f"\n[Notice] Port {port} is already in use by another instance or background process.")
            print(f"To run on another port, use:")
            print(f"  python app.py --port {port + 1}\n")
        else:
            raise
