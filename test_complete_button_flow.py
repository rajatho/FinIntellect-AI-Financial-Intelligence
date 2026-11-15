import requests
import json
import os
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5001"

def test_full_application():
    session = requests.Session()

    print("\n[1] Checking Server Status & Default Gemini Engine...")
    res = session.get(f"{BASE_URL}/api/status")
    assert res.status_code == 200, f"Status failed: {res.status_code}"
    status_data = res.json()
    print(f"Status: {status_data['status']}, Default Model: {status_data['default_model']}, Total Reports: {status_data['total_reports']}")

    print("\n[2] Testing Preloaded Filings / Samples...")
    res = session.get(f"{BASE_URL}/api/samples")
    assert res.status_code == 200
    samples = res.json()["samples"]
    print(f"Loaded {len(samples)} samples:")
    for s in samples:
        print(f" - {s['company']} ({s['reporting_period']}) [{s['industry']}]")

    print("\n[3] Testing Instant Demo Guest Login (Lead CFA Analyst)...")
    res = session.post(f"{BASE_URL}/api/auth/guest-login")
    assert res.status_code == 200
    guest_info = res.json()
    token = guest_info["token"]
    user = guest_info["user"]
    print(f"Logged in as: {user['name']} ({user['email']}) - Role: {user['role']}")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("\n[4] Testing Quick Select Chips / Dynamic Company Analysis...")
    companies = [
        ("NVIDIA Corporation", "Accelerated Computing & AI Hardware", "FY2025", "$"),
        ("Apple Inc.", "Consumer Electronics & Services", "FY2025", "$"),
        ("Tesla, Inc.", "Automotive & Clean Energy", "FY2025", "$"),
        ("Reliance Industries Ltd.", "Energy & Conglomerate", "FY2025", "₹"),
        ("Distressed Retail Corp", "Consumer Retail & E-Commerce", "FY2025", "₹"),
    ]

    last_report_id = None
    for comp, ind, period, cur in companies:
        payload = {
            "company_name": comp,
            "industry": ind,
            "reporting_period": period,
            "currency": cur,
            "length": "Standard",
            "tone": "Professional"
        }
        res = session.post(f"{BASE_URL}/api/analyze", json=payload, headers=headers)
        assert res.status_code == 200, f"Analysis failed for {comp}: {res.text}"
        data = res.json()["data"]
        v_obj = data["verified_object"]
        summary = data["summary"]
        last_report_id = data["report_id"]

        print(f"\n>> {comp} Analyzed Successfully:")
        print(f"   Report ID: {data['report_id']}")
        print(f"   Revenue: {v_obj['financial_metrics']['revenue']['formatted_current']} ({v_obj['financial_metrics']['revenue']['yoy_percent']}% YoY)")
        print(f"   Net Income: {v_obj['financial_metrics']['net_income']['formatted_current']} ({v_obj['financial_metrics']['net_income']['yoy_percent']}% YoY)")
        print(f"   ML Risk Rating: {v_obj['risk_prediction']['class']} ({v_obj['risk_prediction']['probability_formatted']})")
        print(f"   Anomalies Detected: {len(v_obj['anomalies'])}")
        print(f"   Factual Grounding Audit: {summary['validation']['score']}")
        print(f"   Summary Source: {summary['source']}")

    print("\n[5] Testing Length & Tone Summary Regeneration...")
    for length in ["Short", "Detailed"]:
        for tone in ["Executive", "Academic"]:
            payload = {
                "report_id": last_report_id,
                "length": length,
                "tone": tone
            }
            res = session.post(f"{BASE_URL}/api/regenerate", json=payload, headers=headers)
            assert res.status_code == 200, f"Regenerate failed: {res.text}"
            data = res.json()["data"]
            active_v = data["active_version"]
            print(f"   Generated {active_v['version_label']} ({length} / {tone}): Validation = {active_v['validation']['score']}")

    print("\n[6] Testing Version Restore...")
    res = session.post(f"{BASE_URL}/api/version/restore", json={"report_id": last_report_id, "version_num": 1}, headers=headers)
    assert res.status_code == 200
    print(f"   Restored {last_report_id} to Version 1.")

    print("\n[7] Testing Document / Report Export Endpoints...")
    # PDF
    pdf_res = session.get(f"{BASE_URL}/api/reports/{last_report_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("Content-Type") == "application/pdf"
    print(f"   PDF Export Downloaded ({len(pdf_res.content)} bytes).")

    # Markdown Summary
    md_res = session.get(f"{BASE_URL}/api/reports/{last_report_id}/download-summary")
    assert md_res.status_code == 200
    print(f"   Markdown Summary Downloaded ({len(md_res.content)} bytes).")

    # JSON Verified Object
    json_res = session.get(f"{BASE_URL}/api/reports/{last_report_id}/export-json")
    assert json_res.status_code == 200
    print(f"   Verified Object JSON Exported ({len(json_res.content)} bytes).")

    print("\n[8] Testing Report Archive Listing...")
    arch_res = session.get(f"{BASE_URL}/api/reports", headers=headers)
    assert arch_res.status_code == 200
    reports = arch_res.json()["reports"]
    print(f"   Total Archive Reports: {len(reports)}")
    for r in reports[:4]:
        print(f"   - {r['company']} ({r['reporting_period']}): {r['risk_class']} | {r['version_count']} versions")

    print("\n[9] Testing User Profile Retrieval...")
    me_res = session.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()["user"]
    print(f"   Current User: {me_data['name']} (Company: {me_data['company']})")

    print("\n[10] Testing User Logout...")
    logout_res = session.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    print("   Logged out successfully.")

    print("\n=======================================================")
    print("ALL BUTTON FLOWS & DYNAMIC REPORT APIS 100% OPERATIONAL!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_full_application()
