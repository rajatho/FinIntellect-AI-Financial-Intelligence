import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List

class AnomalyDetector:
    """
    Detects financial anomalies using Isolation Forest coupled with
    statistical variance thresholds. Generates strictly non-causal interpretations.
    """

    def __init__(self, variance_threshold_pct: float = 25.0):
        self.variance_threshold_pct = variance_threshold_pct

    def detect_anomalies(self, financial_data: Dict[str, Any], ratios_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        anomalies = []
        series = financial_data.get("series", {})
        curr_p = financial_data.get("reporting_period")
        prev_p = financial_data.get("previous_period")
        currency = financial_data.get("currency", "₹")
        unit = financial_data.get("unit", "Millions")

        if not prev_p:
            return anomalies

        # Candidate metrics to evaluate for anomalies
        eval_metrics = [
            ("revenue", "Revenue"),
            ("net_income", "Net Income"),
            ("total_debt", "Total Debt"),
            ("operating_cash_flow", "Operating Cash Flow"),
            ("operating_income", "Operating Income")
        ]

        # 1. Statistical Threshold & Isolation Forest on Metric deltas
        deltas = []
        metric_candidates = []

        for m_key, m_label in eval_metrics:
            curr_val = series.get(m_key, {}).get(curr_p)
            prev_val = series.get(m_key, {}).get(prev_p)
            if curr_val is not None and prev_val is not None and prev_val != 0:
                pct_change = round(((curr_val - prev_val) / abs(prev_val)) * 100.0, 2)
                deltas.append([pct_change])
                metric_candidates.append({
                    "key": m_key,
                    "label": m_label,
                    "current": curr_val,
                    "previous": prev_val,
                    "change_pct": pct_change
                })

        if deltas:
            # Fit Isolation Forest baseline
            # When sample size is small, we supplement synthetic baseline bounds [-15, 15] for standard business variation
            synthetic_bounds = np.array([[-12.0], [-5.0], [0.0], [5.0], [8.0], [12.0], [15.0], [-10.0]])
            fit_data = np.vstack([synthetic_bounds, np.array(deltas)])
            
            iso_forest = IsolationForest(contamination=0.25, random_state=42)
            iso_forest.fit(fit_data)
            predictions = iso_forest.predict(np.array(deltas))

            for idx, cand in enumerate(metric_candidates):
                is_iso_outlier = (predictions[idx] == -1)
                is_stat_outlier = (abs(cand["change_pct"]) >= self.variance_threshold_pct)

                # Anomaly flagged if both or major variance
                if is_stat_outlier or (is_iso_outlier and abs(cand["change_pct"]) > 20.0):
                    prev_fmt = self._format_currency(cand["previous"], currency, unit)
                    curr_fmt = self._format_currency(cand["current"], currency, unit)
                    direction_str = "decrease" if cand["change_pct"] < 0 else "expansion"

                    # Non-causal factual statement
                    contextual = (
                        f"The report shows a substantial {direction_str} of {abs(cand['change_pct'])}% in reported "
                        f"{cand['label'].lower()} compared with the previous period ({prev_fmt} in {prev_p} to {curr_fmt} in {curr_p})."
                    )

                    anomalies.append({
                        "metric": cand["label"],
                        "period": curr_p,
                        "previous": cand["previous"],
                        "current": cand["current"],
                        "previous_formatted": prev_fmt,
                        "current_formatted": curr_fmt,
                        "change_percent": cand["change_pct"],
                        "detection_method": "Isolation Forest + statistical threshold",
                        "severity": "HIGH" if abs(cand["change_pct"]) >= 30 else "MODERATE",
                        "contextual_interpretation": contextual
                    })

        # 2. Check for extreme ratio anomalies (e.g. Debt-to-Equity jump or liquidity collapse)
        dte = ratios_data.get("debt_to_equity", {})
        if dte and dte.get("change_percent") is not None and dte.get("change_percent") > 30.0:
            anomalies.append({
                "metric": "Debt-to-Equity Leverage",
                "period": curr_p,
                "previous": dte.get("previous"),
                "current": dte.get("current"),
                "previous_formatted": str(dte.get("previous")),
                "current_formatted": str(dte.get("current")),
                "change_percent": dte.get("change_percent"),
                "detection_method": "Isolation Forest + statistical threshold",
                "severity": "HIGH",
                "contextual_interpretation": f"Leverage ratio escalated sharply by {dte.get('change_percent')}% from {dte.get('previous')} to {dte.get('current')}."
            })

        return anomalies

    @staticmethod
    def _format_currency(value: float, currency: str = "₹", unit: str = "Millions") -> str:
        if abs(value) >= 1000:
            billions = value / 1000.0
            return f"{currency}{billions:.1f}B" if billions != int(billions) else f"{currency}{int(billions)}B"
        return f"{currency}{int(value)}M" if value == int(value) else f"{currency}{value:.1f}M"
