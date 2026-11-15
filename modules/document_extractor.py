import json
import os
from typing import Dict, Any, Optional

class DocumentExtractor:
    """
    Handles extraction of raw financial text, tables, and structured data
    from uploaded financial reports (JSON, TXT, CSV, or preloaded filings).
    """

    def __init__(self, sample_dir: str = "data/sample_reports"):
        self.sample_dir = sample_dir

    def extract_from_file(self, filepath: str) -> Dict[str, Any]:
        """Extract financial report document contents based on extension."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        elif ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            return self._parse_text_report(text, os.path.basename(filepath))
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def list_available_samples(self) -> list:
        """List preloaded corporate reports."""
        if not os.path.exists(self.sample_dir):
            return []
        samples = []
        for fname in os.listdir(self.sample_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(self.sample_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        samples.append({
                            "id": fname.replace(".json", ""),
                            "filename": fname,
                            "company": data.get("company_name", "Unknown Corp"),
                            "reporting_period": data.get("reporting_period", "FY2025"),
                            "currency": data.get("currency", "₹"),
                            "industry": data.get("industry", "General")
                        })
                except Exception:
                    pass
        return samples

    def get_sample_by_id(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """Load a sample report by identifier."""
        filename = f"{sample_id}.json" if not sample_id.endswith(".json") else sample_id
        fpath = os.path.join(self.sample_dir, filename)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def create_company_report(
        self,
        company_name: str,
        reporting_period: str = "FY2025",
        industry: str = "Technology & Software",
        currency: str = "$",
        unit: str = "Millions",
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically synthesize a strictly valid, balanced financial statement payload
        for any user-provided corporate entity, adhering to accounting identities.
        """
        company_name = company_name.strip()
        comp_lower = company_name.lower()

        # Preset archetypes for high-profile companies if matched
        if "apple" in comp_lower:
            rev_base, margin, debt_ratio, industry = 385000.0, 0.25, 0.35, "Consumer Electronics & Services"
            currency = "$"
        elif "tesla" in comp_lower:
            rev_base, margin, debt_ratio, industry = 96000.0, 0.08, 0.12, "Electric Vehicles & Clean Energy"
            currency = "$"
        elif "microsoft" in comp_lower:
            rev_base, margin, debt_ratio, industry = 245000.0, 0.36, 0.25, "Cloud Computing & Software"
            currency = "$"
        elif "nvidia" in comp_lower:
            rev_base, margin, debt_ratio, industry = 120000.0, 0.52, 0.15, "Accelerated Computing & AI Hardware"
            currency = "$"
        elif "reliance" in comp_lower:
            rev_base, margin, debt_ratio, industry = 980000.0, 0.09, 0.38, "Conglomerate (Energy, Retail, Telecom)"
            currency = "₹"
        elif "tata" in comp_lower:
            rev_base, margin, debt_ratio, industry = 430000.0, 0.07, 0.45, "Automotive & Industrial Manufacturing"
            currency = "₹"
        elif "retail" in comp_lower:
            rev_base, margin, debt_ratio = 4200.0, -0.04, 0.70
        else:
            # Deterministic seed based on company name
            name_sum = sum(ord(c) for c in company_name)
            rev_base = 2500.0 + (name_sum % 15) * 500.0
            margin = 0.08 + (name_sum % 12) * 0.015
            debt_ratio = 0.25 + (name_sum % 7) * 0.05

        # Apply user overrides if provided
        if custom_metrics:
            if "revenue" in custom_metrics and custom_metrics["revenue"]:
                rev_base = float(custom_metrics["revenue"])
            if "net_margin" in custom_metrics and custom_metrics["net_margin"]:
                margin = float(custom_metrics["net_margin"]) / 100.0

        # Multi-year progression (FY2022 -> FY2025)
        # Prior years progression
        rev_22 = round(rev_base * 0.78, 1)
        rev_23 = round(rev_base * 0.86, 1)
        rev_24 = round(rev_base * 0.93, 1)
        rev_25 = round(rev_base, 1)

        cogs_rate = max(0.35, 1.0 - margin - 0.22)
        opex_rate = 0.20

        def calc_income(rev, net_m):
            cogs = round(rev * cogs_rate, 1)
            gp = round(rev - cogs, 1)
            opex = round(rev * opex_rate, 1)
            op_inc = round(gp - opex, 1)
            int_exp = round(rev * 0.025, 1)
            net_inc = round(rev * net_m, 1)
            tax = round(max(0.0, op_inc - int_exp - net_inc), 1)
            return {
                "revenue": rev,
                "cogs": cogs,
                "gross_profit": gp,
                "operating_expenses": opex,
                "operating_income": op_inc,
                "interest_expense": int_exp,
                "tax_expense": tax,
                "net_income": net_inc
            }

        inc_22 = calc_income(rev_22, margin * 0.85)
        inc_23 = calc_income(rev_23, margin * 0.92)
        inc_24 = calc_income(rev_24, margin * 0.97)
        inc_25 = calc_income(rev_25, margin)

        # Balance Sheet adhering strictly to: Total Assets = Total Liabilities + Equity
        # Total Assets typically ~1.4 - 1.8x Revenue
        assets_24 = round(rev_24 * 1.55, 1)
        assets_25 = round(rev_25 * 1.58, 1)

        total_debt_24 = round(assets_24 * debt_ratio, 1)
        total_debt_25 = round(assets_25 * debt_ratio, 1)

        curr_liab_24 = round(total_debt_24 * 0.35, 1)
        long_debt_24 = round(total_debt_24 * 0.65, 1)
        curr_liab_25 = round(total_debt_25 * 0.36, 1)
        long_debt_25 = round(total_debt_25 * 0.64, 1)

        total_liab_24 = round(curr_liab_24 + long_debt_24 + assets_24 * 0.08, 1)
        total_liab_25 = round(curr_liab_25 + long_debt_25 + assets_25 * 0.08, 1)

        # Exact accounting identity enforced: Equity = Assets - Liabilities
        equity_24 = round(assets_24 - total_liab_24, 1)
        equity_25 = round(assets_25 - total_liab_25, 1)

        # Assets breakdown
        curr_assets_24 = round(assets_24 * 0.34, 1)
        curr_assets_25 = round(assets_25 * 0.35, 1)
        cash_24 = round(curr_assets_24 * 0.40, 1)
        cash_25 = round(curr_assets_25 * 0.42, 1)
        ar_24 = round(curr_assets_24 * 0.35, 1)
        ar_25 = round(curr_assets_25 * 0.34, 1)
        inv_24 = round(curr_assets_24 - cash_24 - ar_24, 1)
        inv_25 = round(curr_assets_25 - cash_25 - ar_25, 1)

        ppe_24 = round(assets_24 * 0.50, 1)
        ppe_25 = round(assets_25 * 0.49, 1)
        intangible_24 = round(assets_24 - curr_assets_24 - ppe_24, 1)
        intangible_25 = round(assets_25 - curr_assets_25 - ppe_25, 1)

        # Cash flow
        ocf_24 = round(inc_24["net_income"] * 1.25, 1)
        ocf_25 = round(inc_25["net_income"] * 1.28, 1)
        capex_24 = round(assets_24 * 0.06, 1)
        capex_25 = round(assets_25 * 0.065, 1)
        fcf_24 = round(ocf_24 - capex_24, 1)
        fcf_25 = round(ocf_25 - capex_25, 1)

        return {
            "company_name": company_name,
            "reporting_period": reporting_period,
            "currency": currency,
            "unit": unit,
            "industry": industry,
            "financial_statements": {
                "income_statement": {
                    "FY2022": inc_22,
                    "FY2023": inc_23,
                    "FY2024": inc_24,
                    "FY2025": inc_25
                },
                "balance_sheet": {
                    "FY2024": {
                        "cash_and_equivalents": cash_24,
                        "accounts_receivable": ar_24,
                        "inventory": inv_24,
                        "current_assets": curr_assets_24,
                        "property_plant_equipment": ppe_24,
                        "intangible_assets": intangible_24,
                        "total_assets": assets_24,
                        "current_liabilities": curr_liab_24,
                        "short_term_debt": round(total_debt_24 * 0.15, 1),
                        "long_term_debt": long_debt_24,
                        "total_debt": total_debt_24,
                        "total_liabilities": total_liab_24,
                        "shareholders_equity": equity_24
                    },
                    "FY2025": {
                        "cash_and_equivalents": cash_25,
                        "accounts_receivable": ar_25,
                        "inventory": inv_25,
                        "current_assets": curr_assets_25,
                        "property_plant_equipment": ppe_25,
                        "intangible_assets": intangible_25,
                        "total_assets": assets_25,
                        "current_liabilities": curr_liab_25,
                        "short_term_debt": round(total_debt_25 * 0.15, 1),
                        "long_term_debt": long_debt_25,
                        "total_debt": total_debt_25,
                        "total_liabilities": total_liab_25,
                        "shareholders_equity": equity_25
                    }
                },
                "cash_flow_statement": {
                    "FY2024": {
                        "operating_cash_flow": ocf_24,
                        "capital_expenditures": capex_24,
                        "free_cash_flow": fcf_24,
                        "financing_cash_flow": round(-ocf_24 * 0.35, 1),
                        "investing_cash_flow": round(-capex_24 * 1.1, 1),
                        "net_change_in_cash": round(cash_25 - cash_24, 1)
                    },
                    "FY2025": {
                        "operating_cash_flow": ocf_25,
                        "capital_expenditures": capex_25,
                        "free_cash_flow": fcf_25,
                        "financing_cash_flow": round(-ocf_25 * 0.38, 1),
                        "investing_cash_flow": round(-capex_25 * 1.15, 1),
                        "net_change_in_cash": round(cash_25 * 0.08, 1)
                    }
                }
            },
            "report_extracts": {
                "management_discussion": [
                    f"{company_name} sustained operational execution throughout {reporting_period}, driven by customer demand and strategic investments.",
                    f"Consolidated revenue reached {currency}{rev_25:,.1f} {unit}, reflecting ongoing market expansion.",
                    f"Operating cash flow reached {currency}{ocf_25:,.1f} {unit}, reinforcing enterprise liquidity resilience."
                ],
                "risk_factors": [
                    f"Macroeconomic volatility and foreign currency fluctuations could influence operating costs.",
                    f"Competitive pressure in the {industry} domain necessitates continued capital commitment.",
                    f"Supply chain dependencies and regulatory adjustments across primary geographical markets."
                ],
                "subsequent_events": [
                    f"Board of Directors authorized capital allocation framework for subsequent fiscal quarters.",
                    f"No material adverse post-balance-sheet events have occurred since the close of {reporting_period}."
                ],
                "auditor_opinion": f"Unqualified Audit Opinion: The financial statements present fairly, in all material respects, the financial position of {company_name} as of {reporting_period}."
            }
        }
