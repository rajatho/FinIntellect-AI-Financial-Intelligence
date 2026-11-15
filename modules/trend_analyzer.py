from typing import Dict, Any, List

class TrendAnalyzer:
    """
    Analyzes multi-year financial trends, verifies consistency, computes CAGR,
    and produces factual observations grounded solely in verified values.
    """

    def analyze_trends(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        series = financial_data.get("series", {})
        currency = financial_data.get("currency", "₹")
        unit = financial_data.get("unit", "Millions")
        periods = financial_data.get("periods", [])

        if len(periods) < 2:
            return []

        trend_metrics = [
            ("revenue", "Revenue Trend"),
            ("net_income", "Net Income Trend"),
            ("operating_income", "Operating Income Trend"),
            ("total_debt", "Total Debt Trend"),
            ("operating_cash_flow", "Operating Cash Flow Trend")
        ]

        trends_output = []

        for metric_key, display_name in trend_metrics:
            vals = series.get(metric_key, {})
            # extract in chronological period order
            history = []
            for p in periods:
                if p in vals and vals[p] is not None:
                    history.append({"period": p, "value": vals[p], "formatted": self._format_currency(vals[p], currency, unit)})

            if len(history) < 2:
                continue

            # Determine consistency
            values_list = [h["value"] for h in history]
            is_consistent_increase = all(values_list[i] < values_list[i+1] for i in range(len(values_list)-1))
            is_consistent_decrease = all(values_list[i] > values_list[i+1] for i in range(len(values_list)-1))

            start_val = values_list[0]
            end_val = values_list[-1]
            years_count = len(values_list) - 1

            cagr = None
            if start_val > 0 and end_val > 0 and years_count > 0:
                cagr = round(((end_val / start_val) ** (1.0 / years_count) - 1.0) * 100.0, 2)

            # Grounded factual observation
            metric_label = display_name.replace(" Trend", "")
            if is_consistent_increase:
                observation = f"{metric_label} increased consistently across the available reporting periods ({history[0]['period']} to {history[-1]['period']})."
                direction = "Consistent Increase"
            elif is_consistent_decrease:
                observation = f"{metric_label} declined consistently across the available reporting periods ({history[0]['period']} to {history[-1]['period']})."
                direction = "Consistent Decline"
            else:
                net_change_pct = round(((end_val - start_val) / abs(start_val)) * 100.0, 1) if start_val != 0 else 0
                dir_word = "net increase" if net_change_pct > 0 else "net decrease"
                observation = f"{metric_label} fluctuated across reporting periods, recording a {dir_word} of {abs(net_change_pct)}% from {history[0]['formatted']} in {history[0]['period']} to {history[-1]['formatted']} in {history[-1]['period']}."
                direction = "Fluctuating"

            trends_output.append({
                "metric": metric_key,
                "title": display_name,
                "history": history,
                "direction": direction,
                "is_consistent": is_consistent_increase or is_consistent_decrease,
                "cagr_percent": cagr,
                "observation": observation,
                "periods_covered": f"{history[0]['period']} - {history[-1]['period']}"
            })

        return trends_output

    @staticmethod
    def _format_currency(value: float, currency: str = "₹", unit: str = "Millions") -> str:
        if abs(value) >= 1000:
            billions = value / 1000.0
            return f"{currency}{billions:.1f}B" if billions != int(billions) else f"{currency}{int(billions)}B"
        return f"{currency}{int(value)}M" if value == int(value) else f"{currency}{value:.1f}M"
