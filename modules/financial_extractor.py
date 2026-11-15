from typing import Dict, Any, List, Optional

class FinancialExtractor:
    """
    Extracts, aligns, and standardizes key financial line items across
    multi-year reporting periods.
    """

    def __init__(self):
        pass

    def extract_metrics(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract multi-year financial metrics from the report data.
        Returns normalized metrics and period-by-period values.
        """
        company = document_data.get("company_name", "Unknown Corporation")
        reporting_period = document_data.get("reporting_period", "FY2025")
        currency = document_data.get("currency", "₹")
        unit = document_data.get("unit", "Millions")
        statements = document_data.get("financial_statements", {})

        income_stmt = statements.get("income_statement", {})
        balance_sheet = statements.get("balance_sheet", {})
        cash_flow = statements.get("cash_flow_statement", {})

        # Find sorted periods
        all_periods = sorted(list(set(
            list(income_stmt.keys()) +
            list(balance_sheet.keys()) +
            list(cash_flow.keys())
        )))

        # Determine current and previous period
        curr_period = reporting_period if reporting_period in all_periods else (all_periods[-1] if all_periods else "FY2025")
        curr_idx = all_periods.index(curr_period) if curr_period in all_periods else len(all_periods) - 1
        prev_period = all_periods[curr_idx - 1] if curr_idx > 0 else None

        # Build metric series
        metrics = {
            "company": company,
            "reporting_period": curr_period,
            "previous_period": prev_period,
            "currency": currency,
            "unit": unit,
            "periods": all_periods,
            "series": {
                "revenue": {},
                "cogs": {},
                "gross_profit": {},
                "operating_income": {},
                "net_income": {},
                "current_assets": {},
                "total_assets": {},
                "current_liabilities": {},
                "total_debt": {},
                "total_liabilities": {},
                "equity": {},
                "operating_cash_flow": {},
                "free_cash_flow": {}
            }
        }

        # Populate series
        for p in all_periods:
            inc = income_stmt.get(p, {})
            bs = balance_sheet.get(p, {})
            cf = cash_flow.get(p, {})

            if "revenue" in inc: metrics["series"]["revenue"][p] = float(inc["revenue"])
            if "cogs" in inc: metrics["series"]["cogs"][p] = float(inc["cogs"])
            if "gross_profit" in inc: metrics["series"]["gross_profit"][p] = float(inc["gross_profit"])
            if "operating_income" in inc: metrics["series"]["operating_income"][p] = float(inc["operating_income"])
            if "net_income" in inc: metrics["series"]["net_income"][p] = float(inc["net_income"])

            if "current_assets" in bs: metrics["series"]["current_assets"][p] = float(bs["current_assets"])
            if "total_assets" in bs: metrics["series"]["total_assets"][p] = float(bs["total_assets"])
            if "current_liabilities" in bs: metrics["series"]["current_liabilities"][p] = float(bs["current_liabilities"])
            if "total_debt" in bs: metrics["series"]["total_debt"][p] = float(bs["total_debt"])
            if "total_liabilities" in bs: metrics["series"]["total_liabilities"][p] = float(bs["total_liabilities"])
            if "shareholders_equity" in bs: metrics["series"]["equity"][p] = float(bs["shareholders_equity"])

            if "operating_cash_flow" in cf: metrics["series"]["operating_cash_flow"][p] = float(cf["operating_cash_flow"])
            if "free_cash_flow" in cf: metrics["series"]["free_cash_flow"][p] = float(cf["free_cash_flow"])

        # Current vs Previous summary with YoY calculations
        metrics["current_summary"] = self._build_current_summary(metrics["series"], curr_period, prev_period, currency, unit)
        return metrics

    def _build_current_summary(self, series: Dict[str, Dict[str, float]], curr: str, prev: str, currency: str, unit: str) -> Dict[str, Any]:
        summary = {}
        for metric_name, val_dict in series.items():
            curr_val = val_dict.get(curr)
            prev_val = val_dict.get(prev) if prev else None
            yoy_pct = None
            yoy_abs = None
            if curr_val is not None and prev_val is not None and prev_val != 0:
                yoy_pct = round(((curr_val - prev_val) / abs(prev_val)) * 100.0, 2)
                yoy_abs = round(curr_val - prev_val, 2)

            summary[metric_name] = {
                "current": curr_val,
                "previous": prev_val,
                "yoy_percent": yoy_pct,
                "yoy_absolute": yoy_abs,
                "formatted_current": self._format_currency(curr_val, currency, unit) if curr_val is not None else "Data unavailable",
                "formatted_previous": self._format_currency(prev_val, currency, unit) if prev_val is not None else "Data unavailable"
            }
        return summary

    @staticmethod
    def _format_currency(value: Optional[float], currency: str = "₹", unit: str = "Millions") -> str:
        if value is None:
            return "Data unavailable"
        # Convert unit display: if value is in Millions and >= 1000, express in B (Billions) or Cr (Crores)
        if abs(value) >= 1000:
            billions = value / 1000.0
            return f"{currency}{billions:.1f}B" if billions != int(billions) else f"{currency}{int(billions)}B"
        return f"{currency}{int(value)}M" if value == int(value) else f"{currency}{value:.1f}M"
