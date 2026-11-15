import os
import json
import requests
from typing import Dict, Any, Optional

class GeminiEngine:
    """
    Dedicated Gemini Financial Report Summarization Engine.
    Uses Gemini 3.5 Flash-Lite / 3.6 Flash with strictly grounded prompt instructions.
    """

    DEFAULT_MODEL = "gemini-3.5-flash-lite"
    DYNAMIC_DEFAULT_KEY = ""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

    def build_prompt(self, verified_obj: Dict[str, Any], length: str = "Standard", tone: str = "Professional", correction_note: Optional[str] = None) -> str:
        """Construct the prompt strictly adhering to specification."""
        length_guidance = {
            "Short": "Keep the entire output concise, approximately 100–150 words.",
            "Standard": "Provide a balanced, thorough summary of approximately 250–400 words.",
            "Detailed": "Provide an in-depth, rigorous multi-section summary of approximately 500–700 words."
        }.get(length, "Provide approximately 250–400 words.")

        tone_guidance = {
            "Professional": "Use objective, balanced, professional financial terminology.",
            "Academic": "Use scholarly, empirical, formal macroeconomic and accounting terminology.",
            "Executive": "Use concise, high-level C-suite strategic framing focused on key risk and capital allocation facts."
        }.get(tone, "Use professional financial terminology.")

        correction_block = ""
        if correction_note:
            correction_block = f"""
CRITICAL CORRECTION REQUIRED FROM PREVIOUS VALIDATION FAILURE:
{correction_note}
You MUST fix these exact discrepancies. Do NOT repeat the errors.
"""

        prompt = f"""You are an AI financial report summarization engine.

Generate a professional financial analysis summary using ONLY the verified information supplied to you in the JSON object below.

STRICT RULES:
1. Never invent financial values.
2. Never estimate missing values.
3. Never change calculated ratios.
4. Never change the machine-learning prediction.
5. Never invent causes for financial changes.
6. Never provide investment advice.
7. Never introduce information not present in the supplied analysis.
8. Clearly distinguish facts, calculated metrics, detected anomalies, and model predictions.
9. If information is unavailable, state "Data unavailable."
10. Keep the summary concise but informative.
11. Use professional financial terminology.
12. Mention the reporting period whenever relevant.
13. Do not exaggerate positive or negative findings.

Length Guideline: {length_guidance}
Tone Guideline: {tone_guidance}
{correction_block}

Generate the summary using EXACTLY the following Markdown structure with clear ## headings:

## Executive Summary
## Financial Performance
## Profitability
## Liquidity
## Solvency
## Efficiency
## Growth
## Risk Analysis
## Anomalies
## Positive Indicators
## Key Financial Insights
## Overall Analytical Assessment

VERIFIED FINANCIAL ANALYSIS OBJECT (INPUT DATA):
```json
{json.dumps(verified_obj, indent=2)}
```

Use actual values supplied in the input. Never invent any facts or reasons.
"""
        return prompt

    def generate_summary(
        self,
        verified_obj: Dict[str, Any],
        length: str = "Standard",
        tone: str = "Professional",
        correction_note: Optional[str] = None,
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calls Gemini 3.5 Flash-Lite to generate the summary.
        """
        api_key = custom_api_key or self.api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY is not set. Please provide an API key in settings.",
                "is_fallback": True
            }

        prompt = self.build_prompt(verified_obj, length, tone, correction_note)

        # Attempt SDK first, fallback to REST API
        text_response = None
        used_model = self.DEFAULT_MODEL
        error_msg = None

        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.95
            )
            response = client.models.generate_content(
                model=used_model,
                contents=prompt,
                config=config
            )
            text_response = response.text
        except Exception as e:
            # Fallback to direct REST API call
            error_msg = str(e)
            try:
                candidate_models = [self.DEFAULT_MODEL, "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
                for candidate in candidate_models:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{candidate}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.2,
                            "topP": 0.95
                        }
                    }
                    res = requests.post(url, json=payload, timeout=30)
                    if res.status_code == 200:
                        res_json = res.json()
                        candidates = res_json.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts:
                                text_response = parts[0].get("text")
                                used_model = candidate
                                break
                    else:
                        error_msg = f"HTTP {res.status_code}: {res.text}"
            except Exception as ex2:
                error_msg = f"SDK failed ({e}) and REST failed ({ex2})"

        if not text_response:
            return {
                "success": False,
                "error": f"Gemini API generation failed: {error_msg}",
                "is_fallback": True
            }

        # Parse sections
        parsed_sections = self._parse_markdown_sections(text_response)

        return {
            "success": True,
            "source": f"Gemini ({used_model})",
            "model": used_model,
            "length": length,
            "tone": tone,
            "full_markdown": text_response,
            "sections": parsed_sections,
            "is_fallback": False
        }

    def _parse_markdown_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        curr_heading = "executive_summary"
        curr_lines = []

        for line in text.split("\n"):
            line_str = line.strip()
            if line_str.startswith("## ") or line_str.startswith("# "):
                heading_title = line_str.lstrip("#").strip().lower().replace(" ", "_")
                if curr_lines:
                    sections[curr_heading] = "\n".join(curr_lines).strip()
                    curr_lines = []
                curr_heading = heading_title
            else:
                curr_lines.append(line)

        if curr_lines:
            sections[curr_heading] = "\n".join(curr_lines).strip()

        return sections
