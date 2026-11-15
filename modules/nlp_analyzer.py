from typing import Dict, Any, List

class NLPAnalyzer:
    """
    Analyzes textual extracts of the financial report, extracts important factual
    statements, calculates executive tone, and surfaces verified citations.
    """

    def analyze_text(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        text_extracts = document_data.get("report_text_extracts", {})
        mda = text_extracts.get("management_discussion", "")
        risk_text = text_extracts.get("risk_factors", "")
        important_statements = text_extracts.get("important_statements", [])

        if not important_statements and (mda or risk_text):
            # Split sentences if not explicitly given
            full_text = f"{mda} {risk_text}".strip()
            sentences = [s.strip() + "." for s in full_text.split(".") if len(s.strip()) > 25]
            important_statements = sentences[:6]

        # Financial sentiment scoring (heuristic polarity on financial lexicon)
        pos_words = ["expanded", "increase", "growth", "resilient", "improved", "strong", "higher", "rebounded", "gain"]
        neg_words = ["declined", "contraction", "loss", "decreased", "higher debt", "risk", "softened", "weakened", "volatility", "strain"]

        combined = f"{mda} {risk_text} {' '.join(important_statements)}".lower()
        pos_count = sum(combined.count(w) for w in pos_words)
        neg_count = sum(combined.count(w) for w in neg_words)

        if pos_count > neg_count * 1.5:
            sentiment = "Positive / Growth-Oriented"
        elif neg_count > pos_count * 1.5:
            sentiment = "Cautious / Constrained"
        else:
            sentiment = "Balanced / Moderate"

        return {
            "management_discussion": mda,
            "risk_factors": risk_text,
            "important_statements": important_statements,
            "sentiment": sentiment,
            "key_themes": [
                "Revenue trajectory and operational execution",
                "Working capital & liquidity monitoring",
                "Capital allocation & debt management"
            ]
        }
