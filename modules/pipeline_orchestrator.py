import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from modules.document_extractor import DocumentExtractor
from modules.financial_extractor import FinancialExtractor
from modules.data_validator import DataValidator
from modules.ratio_calculator import RatioCalculator
from modules.trend_analyzer import TrendAnalyzer
from modules.anomaly_detector import AnomalyDetector
from modules.ml_risk_predictor import MLRiskPredictor
from modules.nlp_analyzer import NLPAnalyzer
from modules.verified_object import VerifiedObjectBuilder
from modules.gemini_engine import GeminiEngine
from modules.validation_engine import ValidationEngine
from modules.fallback_engine import FallbackSummaryEngine
from modules.pdf_generator import ReportPDFGenerator

class PipelineOrchestrator:
    """
    Central orchestration engine for the AI Financial Summary application.
    Executes the entire verified pipeline, coordinates AI generation & validation,
    and maintains version history.
    """

    def __init__(self, store_path: str = "data/report_store.json"):
        self.store_path = store_path
        self.doc_extractor = DocumentExtractor()
        self.fin_extractor = FinancialExtractor()
        self.validator = DataValidator()
        self.ratio_calculator = RatioCalculator()
        self.trend_analyzer = TrendAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.ml_risk_predictor = MLRiskPredictor()
        self.nlp_analyzer = NLPAnalyzer()
        self.verified_builder = VerifiedObjectBuilder()
        self.gemini_engine = GeminiEngine()
        self.validation_engine = ValidationEngine()
        self.fallback_engine = FallbackSummaryEngine()
        self.pdf_generator = ReportPDFGenerator()
        self.store = self._load_store()

    def _load_store(self) -> Dict[str, Any]:
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_store(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, indent=2)

    def run_full_pipeline(
        self,
        document_data: Dict[str, Any],
        report_id: Optional[str] = None,
        length: str = "Standard",
        tone: str = "Professional",
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete end-to-end pipeline:
        Document Extraction -> Financial Data Extraction -> Data Validation ->
        Ratio Calculation -> Trend Analysis -> Anomaly Detection -> ML Risk ->
        NLP Analysis -> Verified Analysis Object -> Gemini 3.5 Flash-Lite / Fallback ->
        Accuracy Validation -> Store Version -> PDF Ready.
        """
        # 1. Extraction & Normalization
        fin_data = self.fin_extractor.extract_metrics(document_data)

        # 2. Accounting Validation
        val_report = self.validator.validate(fin_data)

        # 3. Ratio Calculation
        ratios = self.ratio_calculator.calculate_ratios(fin_data)

        # 4. Trend Analysis
        trends = self.trend_analyzer.analyze_trends(fin_data)

        # 5. Anomaly Detection
        anomalies = self.anomaly_detector.detect_anomalies(fin_data, ratios)

        # 6. ML Risk Prediction
        ml_risk = self.ml_risk_predictor.predict_risk(fin_data, ratios)

        # 7. NLP Analysis
        nlp_res = self.nlp_analyzer.analyze_text(document_data)

        # 8. Build Verified Analysis Object
        verified_obj = self.verified_builder.build(
            financial_data=fin_data,
            ratios_data=ratios,
            trends_data=trends,
            anomalies_data=anomalies,
            ml_risk_data=ml_risk,
            nlp_data=nlp_res
        )

        # Generate unique report key
        company = verified_obj.get("company", "Company")
        period = verified_obj.get("reporting_period", "FY2025")
        rid = report_id or f"{company.replace(' ', '_').lower()}_{period.lower()}"

        # 9. AI Generation with Validation & Retry
        summary_result = self.validation_engine.process_with_retry_and_fallback(
            gemini_engine=self.gemini_engine,
            verified_obj=verified_obj,
            length=length,
            tone=tone,
            custom_api_key=custom_api_key
        )

        # 10. Store in Version History
        version_entry = {
            "version_num": 1,
            "version_label": "Summary v1",
            "created_at": datetime.now().isoformat(),
            "created_at_formatted": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "length": length,
            "tone": tone,
            "source": summary_result.get("source", "Gemini 3.5 Flash-Lite"),
            "model": summary_result.get("model", "gemini-3.5-flash-lite"),
            "is_fallback": summary_result.get("is_fallback", False),
            "validation": summary_result.get("validation", {}),
            "audit_trail": summary_result.get("audit_trail", []),
            "sections": summary_result.get("sections", {}),
            "full_markdown": summary_result.get("full_markdown", "")
        }

        # Update persistent store
        self.store[rid] = {
            "report_id": rid,
            "company": company,
            "reporting_period": period,
            "verified_object": verified_obj,
            "data_validation": val_report,
            "active_version": 1,
            "versions": [version_entry],
            "last_updated": datetime.now().isoformat()
        }
        self._save_store()

        return {
            "report_id": rid,
            "verified_object": verified_obj,
            "data_validation": val_report,
            "summary": version_entry,
            "all_versions": [version_entry]
        }

    def regenerate_summary(
        self,
        report_id: str,
        length: str = "Standard",
        tone: str = "Professional",
        custom_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerates summary ONLY from existing verified analysis object.
        Does not recompute financial metrics.
        Appends new version (Summary v2, Summary v3...).
        """
        report = self.store.get(report_id)
        if not report:
            raise ValueError(f"Report ID '{report_id}' not found.")

        verified_obj = report["verified_object"]
        existing_versions = report.get("versions", [])
        next_ver_num = len(existing_versions) + 1

        # Generate new summary using Gemini or fallback
        summary_result = self.validation_engine.process_with_retry_and_fallback(
            gemini_engine=self.gemini_engine,
            verified_obj=verified_obj,
            length=length,
            tone=tone,
            custom_api_key=custom_api_key
        )

        new_version_entry = {
            "version_num": next_ver_num,
            "version_label": f"Summary v{next_ver_num}",
            "created_at": datetime.now().isoformat(),
            "created_at_formatted": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "length": length,
            "tone": tone,
            "source": summary_result.get("source", "Gemini 3.5 Flash-Lite"),
            "model": summary_result.get("model", "gemini-3.5-flash-lite"),
            "is_fallback": summary_result.get("is_fallback", False),
            "validation": summary_result.get("validation", {}),
            "audit_trail": summary_result.get("audit_trail", []),
            "sections": summary_result.get("sections", {}),
            "full_markdown": summary_result.get("full_markdown", "")
        }

        report["versions"].append(new_version_entry)
        report["active_version"] = next_ver_num
        report["last_updated"] = datetime.now().isoformat()
        self._save_store()

        return {
            "report_id": report_id,
            "verified_object": verified_obj,
            "active_version": new_version_entry,
            "all_versions": report["versions"]
        }

    def restore_version(self, report_id: str, version_num: int) -> Dict[str, Any]:
        """Restores an older summary version to active status."""
        report = self.store.get(report_id)
        if not report:
            raise ValueError("Report not found")
        versions = report.get("versions", [])
        target = next((v for v in versions if v["version_num"] == version_num), None)
        if not target:
            raise ValueError(f"Version {version_num} not found")

        report["active_version"] = version_num
        self._save_store()
        return {
            "report_id": report_id,
            "active_version": target,
            "all_versions": versions
        }

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        report = self.store.get(report_id)
        if not report:
            return None
        active_ver_num = report.get("active_version", 1)
        active_ver = next((v for v in report.get("versions", []) if v["version_num"] == active_ver_num), None)
        if not active_ver and report.get("versions"):
            active_ver = report["versions"][-1]
        return {
            "report_id": report_id,
            "company": report["company"],
            "reporting_period": report["reporting_period"],
            "verified_object": report["verified_object"],
            "data_validation": report.get("data_validation", {}),
            "active_version": active_ver,
            "all_versions": report.get("versions", [])
        }

    def generate_pdf_for_report(self, report_id: str) -> str:
        """Generates the professional 13-section PDF for the active summary version."""
        report = self.get_report(report_id)
        if not report:
            raise ValueError("Report not found")

        verified_obj = report["verified_object"]
        active_summary = report["active_version"]
        validation_obj = active_summary.get("validation", {})

        pdf_path = self.pdf_generator.generate(
            verified_obj=verified_obj,
            summary_obj=active_summary,
            validation_obj=validation_obj
        )
        return pdf_path
