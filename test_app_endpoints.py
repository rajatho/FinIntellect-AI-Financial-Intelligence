import json
from app import app, orchestrator

def test_all():
    client = app.test_client()

    print("\n--- 1. Testing GET / (Index Page) ---")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("PASS: Index HTML rendered successfully.")

    print("\n--- 2. Testing GET /api/samples ---")
    res = client.get("/api/samples")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["samples"]) >= 3
    print(f"PASS: Found {len(data['samples'])} corporate samples.")

    print("\n--- 3. Testing POST /api/analyze (Full Pipeline Execution) ---")
    payload = {
        "sample_id": "techcorp_fy25",
        "length": "Standard",
        "tone": "Professional"
    }
    res = client.post("/api/analyze", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    report_id = data["data"]["report_id"]
    v_obj = data["data"]["verified_object"]
    assert v_obj["company"] == "TechCorp Solutions Ltd."
    assert v_obj["reporting_period"] == "FY2025"
    assert v_obj["risk_prediction"]["class"] == "Moderate Risk"
    assert v_obj["risk_prediction"]["probability_formatted"] == "78%"
    assert len(v_obj["anomalies"]) >= 1
    assert data["data"]["summary"]["validation"]["is_valid"] is True
    print(f"PASS: Full pipeline executed for {report_id}. Risk: {v_obj['risk_prediction']['class']}. Score: {data['data']['summary']['validation']['score']}")

    print("\n--- 4. Testing POST /api/regenerate (Section 16: Summary Regeneration) ---")
    regen_payload = {
        "report_id": report_id,
        "length": "Detailed",
        "tone": "Executive"
    }
    res = client.post("/api/regenerate", json=regen_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["active_version"]["version_label"] == "Summary v2"
    assert len(data["data"]["all_versions"]) >= 2
    print(f"PASS: Regenerated summary as {data['data']['active_version']['version_label']}. Total versions: {len(data['data']['all_versions'])}")

    print("\n--- 5. Testing POST /api/version/restore (Section 17: Restore Version) ---")
    restore_payload = {
        "report_id": report_id,
        "version_num": 1
    }
    res = client.post("/api/version/restore", json=restore_payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["active_version"]["version_num"] == 1
    print("PASS: Restored Summary v1 as active.")

    print("\n--- 6. Testing GET /api/reports/<report_id>/pdf (Section 19: PDF Export) ---")
    res = client.get(f"/api/reports/{report_id}/pdf")
    assert res.status_code == 200
    assert res.content_type == "application/pdf"
    assert len(res.data) > 5000
    print(f"PASS: 13-section PDF exported successfully ({len(res.data)} bytes).")

    print("\n--- 7. Testing GET /api/reports/<report_id>/download-summary ---")
    res = client.get(f"/api/reports/{report_id}/download-summary")
    assert res.status_code == 200
    assert "text/markdown" in res.content_type
    assert b"AI FINANCIAL SUMMARY" in res.data
    print("PASS: Summary Markdown downloaded successfully.")

    print("\n--- 8. Testing GET /api/reports/<report_id>/export-json ---")
    res = client.get(f"/api/reports/{report_id}/export-json")
    assert res.status_code == 200
    assert "application/json" in res.content_type
    json_data = json.loads(res.data)
    assert json_data["company"] == "TechCorp Solutions Ltd."
    print("PASS: Verified analysis JSON exported successfully.")

    print("\n--- 9. Testing Distressed Retail Report Analysis ---")
    payload2 = {
        "sample_id": "distressed_retail_fy25",
        "length": "Standard",
        "tone": "Academic"
    }
    res2 = client.post("/api/analyze", json=payload2)
    assert res2.status_code == 200
    d2 = res2.get_json()["data"]
    assert d2["verified_object"]["risk_prediction"]["class"] == "High Risk"
    assert len(d2["verified_object"]["anomalies"]) >= 2
    print(f"PASS: Distressed scenario accurately classified as High Risk with {len(d2['verified_object']['anomalies'])} anomalies.")

    print("\n--- 10. Testing User Authentication (Login & Guest Access) ---")
    guest_res = client.post("/api/auth/guest-login")
    assert guest_res.status_code == 200
    guest_data = guest_res.get_json()
    assert guest_data["success"] is True
    assert guest_data["user"]["email"] == "analyst@finintellect.com"
    token = guest_data["token"]
    print("PASS: Instant demo analyst login successful.")

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["name"] == "Sarah Jenkins, CFA"
    print("PASS: Verified user profile retrieval.")

    print("\n--- 11. Testing New User Registration & Validation ---")
    reg_res = client.post("/api/auth/register", json={
        "name": "Alexander Sterling",
        "email": f"alex_{int(time.time())}@capital.com",
        "password": "AlphaTrader2025!",
        "company": "Sterling Capital Partners",
        "role": "Portfolio Manager"
    })
    assert reg_res.status_code == 201
    assert reg_res.get_json()["success"] is True
    assert reg_res.get_json()["user"]["role"] == "Portfolio Manager"
    print("PASS: New analyst registration successful.")

    print("\n--- 12. Testing Dynamic Company Name Analysis (User-Inserted Company) ---")
    custom_comp_res = client.post("/api/analyze", json={
        "company_name": "Tesla Motors, Inc.",
        "reporting_period": "FY2025",
        "industry": "Automotive & Clean Energy",
        "currency": "$",
        "length": "Short",
        "tone": "Executive"
    }, headers={"Authorization": f"Bearer {token}"})
    assert custom_comp_res.status_code == 200
    custom_comp_data = custom_comp_res.get_json()
    assert custom_comp_data["success"] is True
    assert custom_comp_data["data"]["verified_object"]["company"] == "Tesla Motors, Inc."
    assert custom_comp_data["data"]["summary"]["validation"]["is_valid"] is True
    print(f"PASS: Dynamic company analysis executed for {custom_comp_data['data']['verified_object']['company']}. Audit Score: {custom_comp_data['data']['summary']['validation']['score']}")

    print("\n==============================================")
    print("ALL 12 TEST SUITES PASSED FLAWLESSLY (100% OK)")
    print("==============================================")

if __name__ == "__main__":
    import time
    test_all()
