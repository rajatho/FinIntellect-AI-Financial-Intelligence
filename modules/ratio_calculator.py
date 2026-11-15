from typing import Dict, Any, Optional

class RatioCalculator:
    """
    Computes key financial ratios across periods, calculates absolute/relative
    changes, and generates mechanical, fact-grounded interpretations.
    """

    def calculate_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        series = financial_data.get("series", {})
        curr_p = financial_data.get("reporting_period")
        prev_p = financial_data.get("previous_period")

        ratios_dict = {}

        # List of target ratios to compute
        ratio_defs = [
            {
                "key": "current_ratio",
                "name": "Current Ratio",
                "category": "Liquidity",
                "calc": lambda p: self._safe_div(series.get("current_assets", {}).get(p), series.get("current_liabilities", {}).get(p)),
                "is_percentage": False,
                "better": "higher",
                "interpret_up": "Liquidity improved",
                "interpret_down": "Liquidity decreased",
                "interpret_same": "Liquidity maintained"
            },
            {
                "key": "quick_ratio",
                "name": "Quick Ratio",
                "category": "Liquidity",
                "calc": lambda p: self._calc_quick_ratio(series, p),
                "is_percentage": False,
                "better": "higher",
                "interpret_up": "Immediate liquidity strengthened",
                "interpret_down": "Immediate liquidity softened",
                "interpret_same": "Quick liquidity stable"
            },
            {
                "key": "debt_to_equity",
                "name": "Debt-to-Equity",
                "category": "Solvency",
                "calc": lambda p: self._safe_div(series.get("total_debt", {}).get(p), series.get("equity", {}).get(p)),
                "is_percentage": False,
                "better": "lower",
                "interpret_up": "Leverage increased",
                "interpret_down": "Leverage reduced / deleveraged",
                "interpret_same": "Leverage unchanged"
            },
            {
                "key": "debt_to_assets",
                "name": "Debt-to-Assets",
                "category": "Solvency",
                "calc": lambda p: self._safe_div(series.get("total_debt", {}).get(p), series.get("total_assets", {}).get(p)),
                "is_percentage": False,
                "better": "lower",
                "interpret_up": "Debt load expanded",
                "interpret_down": "Debt proportion decreased",
                "interpret_same": "Solvency profile steady"
            },
            {
                "key": "net_profit_margin",
                "name": "Net Profit Margin",
                "category": "Profitability",
                "calc": lambda p: self._safe_pct(series.get("net_income", {}).get(p), series.get("revenue", {}).get(p)),
                "is_percentage": True,
                "better": "higher",
                "interpret_up": "Profit margin expanded",
                "interpret_down": "Profitability compressed",
                "interpret_same": "Margin unchanged"
            },
            {
                "key": "roe",
                "name": "Return on Equity (ROE)",
                "category": "Profitability",
                "calc": lambda p: self._safe_pct(series.get("net_income", {}).get(p), series.get("equity", {}).get(p)),
                "is_percentage": True,
                "better": "higher",
                "interpret_up": "Return improved",
                "interpret_down": "Return decreased",
                "interpret_same": "Return stable"
            },
            {
                "key": "roa",
                "name": "Return on Assets (ROA)",
                "category": "Profitability",
                "calc": lambda p: self._safe_pct(series.get("net_income", {}).get(p), series.get("total_assets", {}).get(p)),
                "is_percentage": True,
                "better": "higher",
                "interpret_up": "Asset return increased",
                "interpret_down": "Asset return decreased",
                "interpret_same": "Asset yield unchanged"
            },
            {
                "key": "operating_margin",
                "name": "Operating Margin",
                "category": "Profitability",
                "calc": lambda p: self._safe_pct(series.get("operating_income", {}).get(p), series.get("revenue", {}).get(p)),
                "is_percentage": True,
                "better": "higher",
                "interpret_up": "Operating efficiency rose",
                "interpret_down": "Operating margin narrowed",
                "interpret_same": "Operating margin steady"
            }
        ]

        for item in ratio_defs:
            curr_val = item["calc"](curr_p)
            prev_val = item["calc"](prev_p) if prev_p else None

            change_pct = None
            change_pp = None
            interpretation = "Data unavailable"

            if curr_val is not None and prev_val is not None:
                if item["is_percentage"]:
                    change_pp = round(curr_val - prev_val, 2)
                    change_pct = round(((curr_val - prev_val) / abs(prev_val)) * 100.0, 2) if prev_val != 0 else None
                    if change_pp > 0:
                        interpretation = item["interpret_up"]
                    elif change_pp < 0:
                        interpretation = item["interpret_down"]
                    else:
                        interpretation = item["interpret_same"]
                else:
                    change_abs = round(curr_val - prev_val, 2)
                    change_pct = round(((curr_val - prev_val) / abs(prev_val)) * 100.0, 2) if prev_val != 0 else None
                    if change_abs > 0:
                        interpretation = item["interpret_up"]
                    elif change_abs < 0:
                        interpretation = item["interpret_down"]
                    else:
                        interpretation = item["interpret_same"]
            elif curr_val is not None:
                interpretation = "Baseline period observation"

            formatted_change = "N/A"
            if item["is_percentage"]:
                if change_pp is not None:
                    formatted_change = f"{'+' if change_pp > 0 else ''}{change_pp:.1f} pp"
            else:
                if change_pct is not None:
                    formatted_change = f"{'+' if change_pct > 0 else ''}{change_pct:.1f}%"

            ratios_dict[item["key"]] = {
                "name": item["name"],
                "category": item["category"],
                "current": round(curr_val, 2) if curr_val is not None else None,
                "previous": round(prev_val, 2) if prev_val is not None else None,
                "change_percent": change_pct,
                "change_pp": change_pp,
                "formatted_current": self._format_ratio(curr_val, item["is_percentage"]),
                "formatted_previous": self._format_ratio(prev_val, item["is_percentage"]),
                "formatted_change": formatted_change,
                "interpretation": interpretation
            }

        return ratios_dict

    def _calc_quick_ratio(self, series: Dict[str, Dict[str, float]], period: Optional[str]) -> Optional[float]:
        if not period:
            return None
        ca = series.get("current_assets", {}).get(period)
        cl = series.get("current_liabilities", {}).get(period)
        if ca is None or cl is None or cl == 0:
            return None
        # Default inventory deduction if available
        inv = ca * 0.25 # conservative proxy if inventory not separated
        return round((ca - inv) / cl, 2)

    def _safe_div(self, num: Optional[float], den: Optional[float]) -> Optional[float]:
        if num is None or den is None or den == 0:
            return None
        return round(num / den, 2)

    def _safe_pct(self, num: Optional[float], den: Optional[float]) -> Optional[float]:
        if num is None or den is None or den == 0:
            return None
        return round((num / den) * 100.0, 2)

    def _format_ratio(self, val: Optional[float], is_percentage: bool) -> str:
        if val is None:
            return "N/A"
        return f"{val:.1f}%" if is_percentage else f"{val:.2f}"
