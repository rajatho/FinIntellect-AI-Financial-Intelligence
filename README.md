# 📊 FinIntellect: Advanced AI Financial Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash%20%7C%202.5%20Pro-4285F4.svg)](https://deepmind.google/technologies/gemini/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Ensemble%20ML-F7931E.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

FinIntellect is an enterprise-grade AI financial intelligence and corporate analysis platform. It combines **Google Gemini 2.5 Flash / 2.5 Pro**, a **Heterogeneous Machine Learning Voting Ensemble** (Gradient Boosting, Random Forest, and Calibrated Logistic Regression), **Altman Z''-Score & Piotroski F-Score Econometric Engines**, **Isolation Forest Anomaly Detection**, and an offline **Deterministic Python Fallback Engine**.

The system enforces **zero-hallucination fact grounding**, 7-point automated accuracy auditing, multi-version comparison history, executive audio briefings, CSV data export, and professional 13-section PDF reports.

> 📖 **Detailed Technical Specification**: For an in-depth mathematical and algorithmic breakdown of every model and equation, see [MODEL_ARCHITECTURE_AND_WORKFLOW.md](MODEL_ARCHITECTURE_AND_WORKFLOW.md).

---

## 🚀 Final Workflow Architecture

```text
Financial Report / Filing (JSON or Custom Corporate Profile)
                           ↓
Document & Filing Extraction
                           ↓
Financial Metric Normalization (Revenue, Net Income, Assets, Debt, Cash Flow)
                           ↓
Accounting Identity Audit (Assets = Liabilities + Equity)
                           ↓
Deterministic Ratio Calculation (CR, QR, D/E, ROE, ROA, Net Margin)
                           ↓
Trend Analysis (Multi-Year Directional Consistency & CAGR)
                           ↓
Anomaly Detection (Isolation Forest + Statistical Variance > 25%)
                           ↓
Multi-Model Solvency Ensemble (Gradient Boosting + Random Forest + Logistic Regression)
                           ↓
Econometric Distress Scoring (Altman Z''-Score & Piotroski F-Score)
                           ↓
NLP Disclosure Sentiment & Management Statements Analysis
                           ↓
Verified Analysis Object (Strict JSON Single Source of Truth)
                           ↓
Gemini 2.5 Flash / 2.5 Pro / Deterministic Fallback Engine
                           ↓
7-Point Automated Factual Accuracy Validation Audit
                           ↓
AI Financial Summary (Short | Standard | Detailed; Professional | Academic | Executive)
                           ↓
Multi-Channel Delivery:
  • Interactive Dashboard (Speedometers, Consensus Matrix, XAI Weights)
  • Executive Audio Briefing (Natural Voice Speech Synthesis)
  • 1-Click CSV / Excel Data Export
  • Multi-Page 13-Section PDF ReportLab Export
```

---

## 🧠 AI Models & Purpose Matrix

| Model Architecture | Purpose in FinIntellect | Why This Model Was Chosen |
| :--- | :--- | :--- |
| **Gemini 2.5 Flash** | Primary Summary Generation | Fast sub-second response, excellent adherence to negative constraints and factual prompt grounding. |
| **Gemini 2.5 Pro** | Deep Institutional Synthesis | Highest reasoning capacity for complex balance sheet transformations and multi-year restructuring filings. |
| **Gemini 3.5 Flash-Lite** | Real-Time Diagnostics | Ultra-low latency generation for fast mobile and bandwidth-restricted scenarios. |
| **Gradient Boosting Classifier** | Solvency Risk Classification | Sequential tree boosting capturing subtle non-linear shifts in working capital and margins. |
| **Random Forest Classifier** | Solvency Risk Consensus | 50 bootstrap-aggregated decision trees mitigating cyclical variance and overfitting. |
| **Logistic Regression** | Probabilistic Calibration | L2-regularized linear decision model providing monotonic, well-calibrated posterior probabilities. |
| **Altman Z''-Score Engine** | Credit Risk Rating | Globally benchmarked credit scoring model (NYU Stern) outputting Safe, Grey, or Distress zones. |
| **Piotroski F-Score Index** | Fundamental Health Score | 9-point fundamental accounting rubric assessing Profitability, Leverage, and Operational Efficiency. |
| **Isolation Forest** | Financial Anomaly Detection | Unsupervised outlier isolation identifying irregular spikes or abnormal YoY movements without labels. |
| **Deterministic Fallback Engine** | Offline / Zero Downtime | 100% deterministic Python template summary guaranteeing zero downtime and complete fact grounding. |

---

## 🛠 Features & Specification Compliance

| Specification | Implementation Detail | Status |
|---|---|:---:|
| **1. Fact-Grounded Synthesis** | Summaries use **only** verified extracted values, calculated ratios, verified trends, detected anomalies, ML prediction, and explicit report statements. Zero invented facts or causes. | Verified |
| **2. Verified Analysis Object** | Strict JSON schema containing `financial_metrics`, `ratios`, `trends`, `anomalies`, `risk_prediction`, `positive_indicators`, `risk_indicators`, and `important_statements`. | Verified |
| **3. Dedicated Gemini Prompt** | 13 strict rules enforcing no invented values, no changes to calculated ratios or ML predictions, structured 12-section layout. | Verified |
| **4. Summary Page UI** | Complete dedicated page with top header, company, period, engine badge, and functioning action buttons: `Regenerate Summary`, `Copy Summary`, `Download Summary`, and `Export Full Report`. | Verified |
| **5. Executive Summary Card** | Visual card with factual numbers, ML risk classification, and attention areas. Features subtle visual tags: `[Calculated]`, `[ML]`, `[AI Insight]`. | Verified |
| **6. Performance Summary** | Revenue, revenue growth, net income, profit growth, assets, debt, operating cash flow with factual non-speculative interpretations. | Verified |
| **7. Ratio Summary Table** | Current, Previous, Change (% / pp), and mechanical interpretations for Current Ratio, Quick Ratio, Debt-to-Equity, ROE, ROA, Net Profit Margin, etc. | Verified |
| **8. Trend Summary** | Multi-year progression charts (Chart.js) and strict consistency checks (only calls a trend consistent if every step increases/decreases). | Verified |
| **9. Anomaly Summary** | Isolation Forest + statistical thresholding (>25% YoY variance), previous vs. current values, and non-causal contextual interpretations. | Verified |
| **10. ML Risk Assessment** | Gradient Boosting + Random Forest + Logistic Regression ensemble + Altman Z''-Score + Piotroski F-Score. | Verified |
| **11. Positive Indicators** | Auto-detected verified positive movements (or "No significant positive indicators were identified from the available data"). | Verified |
| **12. Key Risk Indicators** | Data-supported risk indicators (debt expansion, profit compression, falling liquidity, etc.). | Verified |
| **13. Analytical Assessment** | Grounded synthesis with mandatory regulatory and non-investment advice disclaimer. | Verified |
| **14. Summary Length** | User-selectable: **Short** (100–150w), **Standard** (250–400w), **Detailed** (500–700w). | Verified |
| **15. Analytical Tone** | User-selectable: **Professional** (default), **Academic**, **Executive**. | Verified |
| **16. AI Model Switcher** | 1-click model selection: Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 3.5 Lite, Deterministic Python Engine. | Verified |
| **17. Executive Audio Briefing** | Natural speech synthesis with audio wave animation for executive listening on the go. | Verified |
| **18. Version History** | Stores `Summary v1`, `Summary v2`, `Summary v3`... with **View**, **Compare**, **Restore**, and **Download**. | Verified |
| **19. 13-Section PDF Report** | Multi-page ReportLab PDF matching exact Section 19 order with running headers, footers with page numbering (Page X of Y), and tables. | Verified |
| **20. 1-Click CSV Export** | Export complete balance sheet and ratio datasets into standard RFC 4180 CSV spreadsheet format. | Verified |
| **21. Accuracy Validation** | 7-point automated audit checking financial values, ratios, ML risk class, percentages, years, company facts, and no invented causes. | Verified |
| **22. Deterministic Fallback** | 100% deterministic Python template summary guaranteeing zero downtime and complete fact grounding offline. | Verified |

---

## 🏃 Quick Start Guide

### 1. Run Application
```powershell
# Navigate to project folder
Set-Location "C:\Users\ASUS\.gemini\antigravity\scratch\financial_summary_app"

# Start FinIntellect
& ".\.venv\Scripts\python.exe" app.py
```
Open your browser at **[http://127.0.0.1:5001](http://127.0.0.1:5001)**.

### 2. Optional: Configure Gemini API Key
You can either:
- Set it in your PowerShell environment:
  ```powershell
  $env:GEMINI_API_KEY = "your-gemini-api-key"
  ```
- Or enter it directly in the web UI.

*If no key is configured, the system automatically uses the **Python Deterministic Fallback Engine**, which produces 100% verified, 7-point audit-passing summaries.*

### 3. Run Automated Tests
```powershell
.\.venv\Scripts\python.exe test_app_endpoints.py
```

---

## 📄 License
This project is licensed under the MIT License.
