from modules.document_extractor import DocumentExtractor
from modules.pipeline_orchestrator import PipelineOrchestrator

def main():
    print("Testing Pipeline Orchestration...")
    extractor = DocumentExtractor()
    sample = extractor.get_sample_by_id("techcorp_fy25")
    if not sample:
        print("Sample not found!")
        return

    orchestrator = PipelineOrchestrator()
    result = orchestrator.run_full_pipeline(
        document_data=sample,
        report_id="techcorp_solutions_ltd._fy2025",
        length="Standard",
        tone="Professional"
    )

    print("Pipeline Execution Successful!")
    print(f"Company: {result['verified_object']['company']}")
    print(f"Period: {result['verified_object']['reporting_period']}")
    print(f"ML Risk: {result['verified_object']['risk_prediction']['class']} ({result['verified_object']['risk_prediction']['probability_formatted']})")
    print(f"Anomalies: {len(result['verified_object']['anomalies'])}")
    print(f"Summary Source: {result['summary']['source']}")
    print(f"Active Version: {result['summary']['version_label']}")
    print(f"Validation Score: {result['summary']['validation']['score']}")

    # Test PDF generation
    pdf_path = orchestrator.generate_pdf_for_report("techcorp_solutions_ltd._fy2025")
    print(f"PDF Generated Successfully at: {pdf_path}")

if __name__ == "__main__":
    main()
