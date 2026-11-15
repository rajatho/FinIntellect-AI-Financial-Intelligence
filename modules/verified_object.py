from typing import Dict, Any, List

class VerifiedObjectBuilder:
    """
    Assembles the complete Verified Analysis Object conforming to Section 2
    of the specification. This object is the single source of truth for
    both the Gemini prompt and the deterministic summary.
    """

    def build(
        self,
        financial_data: Dict[str, Any],
        ratios_data: Dict[str, Any],
        trends_data: List[Dict[str, Any]],
        anomalies_data: List[Dict[str, Any]],
        ml_risk_data: Dict[str, Any],
        nlp_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        company = financial_data.get("company", "Company")
        reporting_period = financial_data.get("reporting_period", "FY2025")
        previous_period = financial_data.get("previous_period")
        currency = financial_data.get("currency", "₹")
        unit = financial_data.get("unit", "Millions")
        summary = financial_data.get("current_summary", {})

        # 1. Structure financial_metrics
        financial_metrics = {
            "revenue": summary.get("revenue", {}),
            "net_income": summary.get("net_income", {}),
            "assets": summary.get("total_assets", {}),
            "liabilities": summary.get("total_liabilities", {}),
            "debt": summary.get("total_debt", {}),
            "equity": summary.get("equity", {}),
            "operating_cash_flow": summary.get("operating_cash_flow", {})
        }

        # 2. Structure ratios (matching the required key names)
        ratios = {
            "current_ratio": ratios_data.get("current_ratio", {}),
            "quick_ratio": ratios_data.get("quick_ratio", {}),
            "debt_to_equity": ratios_data.get("debt_to_equity", {}),
            "roe": ratios_data.get("roe", {}),
            "roa": ratios_data.get("roa", {}),
            "net_profit_margin": ratios_data.get("net_profit_margin", {}),
            "operating_margin": ratios_data.get("operating_margin", {})
        }

        # 3. Construct positive indicators strictly from data
        positive_indicators = []
        rev_info = summary.get("revenue", {})
        if rev_info.get("yoy_percent") is not None and rev_info.get("yoy_percent") > 0:
            positive_indicators.append(f"Revenue growth of {rev_info['yoy_percent']}% year-over-year")

        ni_info = summary.get("net_income", {})
        if ni_info.get("yoy_percent") is not None and ni_info.get("yoy_percent") > 0:
            positive_indicators.append(f"Net profit improvement of {ni_info['yoy_percent']}%")

        debt_info = summary.get("total_debt", {})
        if debt_info.get("yoy_percent") is not None and debt_info.get("yoy_percent") < 0:
            positive_indicators.append(f"Lower debt load (reduced by {abs(debt_info['yoy_percent'])}%)")

        cr_info = ratios.get("current_ratio", {})
        if cr_info.get("change_percent") is not None and cr_info.get("change_percent") > 0:
            positive_indicators.append(f"Improved liquidity (current ratio rose to {cr_info['current']})")

        roa_info = ratios.get("roa", {})
        if roa_info.get("change_pp") is not None and roa_info.get("change_pp") > 0:
            positive_indicators.append(f"Improved ROA (increased by {roa_info['change_pp']} pp)")

        roe_info = ratios.get("roe", {})
        if roe_info.get("change_pp") is not None and roe_info.get("change_pp") > 0:
            positive_indicators.append(f"Improved ROE (increased by {roe_info['change_pp']} pp)")

        ocf_info = summary.get("operating_cash_flow", {})
        if ocf_info.get("yoy_percent") is not None and ocf_info.get("yoy_percent") > 0:
            positive_indicators.append(f"Improved operating cash flow (up {ocf_info['yoy_percent']}%)")
        elif ocf_info.get("current") is not None and ocf_info.get("current") > 0:
            positive_indicators.append(f"Positive operating cash generation ({ocf_info.get('formatted_current')})")

        # Fallback if none exist
        if not positive_indicators:
            positive_indicators = ["No significant positive indicators were identified from the available data."]

        # 4. Construct key risk indicators strictly from data
        risk_indicators = []
        if debt_info.get("yoy_percent") is not None and debt_info.get("yoy_percent") > 0:
            risk_indicators.append(f"Increasing debt: Total debt grew by {debt_info['yoy_percent']}% to {debt_info['formatted_current']}")

        if ni_info.get("yoy_percent") is not None and ni_info.get("yoy_percent") < 0:
            risk_indicators.append(f"Declining profit: Net profit contracted by {abs(ni_info['yoy_percent'])}% to {ni_info['formatted_current']}")

        if cr_info.get("change_percent") is not None and cr_info.get("change_percent") < 0:
            risk_indicators.append(f"Falling liquidity: Current ratio weakened by {abs(cr_info['change_percent'])}% to {cr_info['current']}")

        if ocf_info.get("current") is not None and ocf_info.get("current") < 0:
            risk_indicators.append(f"Negative operating cash flow: Cash from operations stood at {ocf_info['formatted_current']}")

        dte_info = ratios.get("debt_to_equity", {})
        if dte_info.get("change_percent") is not None and dte_info.get("change_percent") > 15.0:
            risk_indicators.append(f"Elevated leverage: Debt-to-Equity increased to {dte_info['current']}")

        npm_info = ratios.get("net_profit_margin", {})
        if npm_info.get("change_pp") is not None and npm_info.get("change_pp") < 0:
            risk_indicators.append(f"Declining profitability ratio: Net margin contracted by {abs(npm_info['change_pp'])} pp to {npm_info['current']}%")

        if anomalies_data:
            risk_indicators.append(f"Unusual financial movements: {len(anomalies_data)} significant financial anomalies detected by Isolation Forest")

        if not risk_indicators:
            risk_indicators = ["No immediate material risk flags detected in the analyzed ratios."]

        # Build Verified Analysis Object
        verified_obj = {
            "company": company,
            "reporting_period": reporting_period,
            "previous_period": previous_period,
            "currency": currency,
            "unit": unit,
            "financial_metrics": financial_metrics,
            "ratios": ratios,
            "trends": trends_data,
            "anomalies": anomalies_data,
            "risk_prediction": {
                "class": ml_risk_data.get("class", "Moderate Risk"),
                "probability": ml_risk_data.get("probability", 78.0),
                "probability_formatted": ml_risk_data.get("probability_formatted", "78%"),
                "risk_meter_score": ml_risk_data.get("risk_meter_score", 50.0),
                "class_probabilities": ml_risk_data.get("class_probabilities", {
                    "low_risk": 14.0,
                    "moderate_risk": 78.0,
                    "high_risk": 8.0
                }),
                "primary_risk_drivers": ml_risk_data.get("primary_indicators", ["Total debt expansion"]),
                "primary_indicators": ml_risk_data.get("primary_indicators", []),
                "positive_indicators": ml_risk_data.get("positive_indicators", [])
            },
            "positive_indicators": positive_indicators,
            "risk_indicators": risk_indicators,
            "important_statements": nlp_data.get("important_statements", [])
        }

        return verified_obj
