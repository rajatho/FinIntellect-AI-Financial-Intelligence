from typing import Dict, Any, List

class DataValidator:
    """
    Validates extracted financial data against accounting identities,
    sanity checks, and completeness rules.
    """

    def __init__(self, tolerance_pct: float = 2.0):
        self.tolerance_pct = tolerance_pct

    def validate(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates accounting identities and integrity.
        Returns a detailed audit report.
        """
        checks = []
        errors = []
        warnings = []
        series = financial_data.get("series", {})
        curr_period = financial_data.get("reporting_period")

        # 1. Non-negative Revenue
        rev_curr = series.get("revenue", {}).get(curr_period)
        if rev_curr is not None:
            if rev_curr >= 0:
                checks.append({"name": "Revenue Positivity", "status": "PASSED", "detail": f"Revenue is non-negative: {rev_curr}"})
            else:
                errors.append(f"Negative revenue detected in {curr_period}: {rev_curr}")
                checks.append({"name": "Revenue Positivity", "status": "FAILED", "detail": f"Negative revenue: {rev_curr}"})
        else:
            warnings.append(f"Revenue data missing for {curr_period}")
            checks.append({"name": "Revenue Positivity", "status": "WARNING", "detail": "Revenue data missing"})

        # 2. Accounting Balance Sheet Identity: Total Assets == Total Liabilities + Shareholders Equity
        assets = series.get("total_assets", {}).get(curr_period)
        liabilities = series.get("total_liabilities", {}).get(curr_period)
        equity = series.get("equity", {}).get(curr_period)

        if assets is not None and liabilities is not None and equity is not None:
            claims = liabilities + equity
            discrepancy = abs(assets - claims)
            allowed_tol = (assets * (self.tolerance_pct / 100.0))
            if discrepancy <= allowed_tol:
                checks.append({
                    "name": "Balance Sheet Identity (A = L + E)",
                    "status": "PASSED",
                    "detail": f"Assets ({assets}) matches Liabilities + Equity ({claims}) within {self.tolerance_pct}% tolerance"
                })
            else:
                warnings.append(f"Balance sheet discrepancy: Assets ({assets}) != Liabilities + Equity ({claims}). Delta: {round(discrepancy, 2)}")
                checks.append({
                    "name": "Balance Sheet Identity (A = L + E)",
                    "status": "WARNING",
                    "detail": f"Discrepancy of {round(discrepancy, 2)} detected"
                })
        else:
            checks.append({
                "name": "Balance Sheet Identity (A = L + E)",
                "status": "INFO",
                "detail": "Partial balance sheet items provided"
            })

        # 3. Income Statement Consistency: Gross Profit == Revenue - COGS
        cogs = series.get("cogs", {}).get(curr_period)
        gross_profit = series.get("gross_profit", {}).get(curr_period)
        if rev_curr is not None and cogs is not None and gross_profit is not None:
            calc_gp = rev_curr - cogs
            if abs(calc_gp - gross_profit) <= (rev_curr * 0.01):
                checks.append({"name": "Gross Profit Consistency", "status": "PASSED", "detail": f"Gross Profit {gross_profit} matches Revenue - COGS"})
            else:
                warnings.append(f"Gross profit discrepancy: {gross_profit} vs calculated {calc_gp}")
                checks.append({"name": "Gross Profit Consistency", "status": "WARNING", "detail": "Minor gross profit variance"})

        # 4. Period Continuity Check
        periods = financial_data.get("periods", [])
        if len(periods) >= 2:
            checks.append({"name": "Multi-Period Availability", "status": "PASSED", "detail": f"{len(periods)} reporting periods available for comparative analysis: {', '.join(periods)}"})
        else:
            warnings.append("Less than 2 reporting periods available. Comparative growth cannot be fully computed.")
            checks.append({"name": "Multi-Period Availability", "status": "WARNING", "detail": "Single period analysis only"})

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "status": "VERIFIED" if is_valid and len(warnings) == 0 else ("VERIFIED_WITH_WARNINGS" if is_valid else "VALIDATION_FAILED"),
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
            "checked_period": curr_period
        }
