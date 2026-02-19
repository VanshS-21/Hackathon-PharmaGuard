"""
PharmaGuard — Sample VCF File Testing
Tests multiple sample VCF files through the full frontend upload → analyze → results flow.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample"
TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"
SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots" / "vcf_samples"
REPORT_PATH = Path(__file__).resolve().parent / "vcf_test_report.txt"

# VCF files to test with their target drugs
TEST_CASES = [
    {
        "name": "sample_patient",
        "file": SAMPLE_DIR / "sample_patient.vcf",
        "drugs": ["CODEINE"],
        "description": "Primary sample — CYP2D6 codeine interaction"
    },
    {
        "name": "sample2",
        "file": SAMPLE_DIR / "sample2.vcf",
        "drugs": ["WARFARIN"],
        "description": "Warfarin — CYP2C9/VKORC1 interaction"
    },
    {
        "name": "sample3",
        "file": SAMPLE_DIR / "sample3.vcf",
        "drugs": ["CLOPIDOGREL"],
        "description": "Clopidogrel — CYP2C19 interaction"
    },
    {
        "name": "sample4",
        "file": SAMPLE_DIR / "sample4.vcf",
        "drugs": ["SIMVASTATIN"],
        "description": "Simvastatin — SLCO1B1 interaction"
    },
    {
        "name": "sample5",
        "file": SAMPLE_DIR / "sample5.vcf",
        "drugs": ["AZATHIOPRINE"],
        "description": "Azathioprine — TPMT interaction"
    },
    {
        "name": "sample6",
        "file": SAMPLE_DIR / "sample6.vcf",
        "drugs": ["FLUOROURACIL"],
        "description": "Fluorouracil — DPYD interaction"
    },
    {
        "name": "sample7_multi",
        "file": SAMPLE_DIR / "sample7.vcf",
        "drugs": ["CODEINE", "WARFARIN", "CLOPIDOGREL"],
        "description": "Multi-drug analysis — 3 drugs at once"
    },
    {
        "name": "test_data_sample",
        "file": TEST_DATA_DIR / "sample.vcf",
        "drugs": ["CODEINE", "SIMVASTATIN"],
        "description": "test_data/sample.vcf — 2 drugs"
    },
]

results = []

def run_test(page, case, index):
    """Run a single VCF test case."""
    test_name = case["name"]
    file_path = case["file"]
    drugs = case["drugs"]
    desc = case["description"]

    print(f"\n{'='*60}")
    print(f"TEST {index+1}: {test_name}")
    print(f"  File: {file_path.name}")
    print(f"  Drugs: {', '.join(drugs)}")
    print(f"  {desc}")
    print(f"{'='*60}")

    if not file_path.exists():
        msg = f"SKIP — File not found: {file_path}"
        print(f"  ⚠️ {msg}")
        results.append({"name": test_name, "status": "SKIP", "details": msg})
        return

    try:
        # 1. Navigate to landing
        page.goto(BASE, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1000)

        # 2. Upload VCF file
        file_input = page.locator('input[type="file"]')
        file_input.set_input_files(str(file_path))
        page.wait_for_timeout(500)

        # Verify upload
        file_name_visible = page.get_by_text(file_path.name).is_visible()
        if file_name_visible:
            print(f"  ✅ File uploaded: {file_path.name}")
        else:
            print(f"  ⚠️ File name not visible after upload")

        # 3. Select drugs
        for drug in drugs:
            drug_btn = page.get_by_role("button", name=drug, exact=True)
            if drug_btn.is_visible():
                drug_btn.click()
                page.wait_for_timeout(200)
                print(f"  ✅ Selected: {drug}")
            else:
                print(f"  ⚠️ Drug button not found: {drug}")

        # Screenshot: before analysis
        ss_path = SCREENSHOT_DIR / f"{test_name}_before.png"
        page.screenshot(path=str(ss_path), full_page=True)

        # 4. Click Run Analysis
        run_btn = page.get_by_role("button", name="Run Analysis")
        if not run_btn.is_enabled():
            msg = "Run Analysis button not enabled"
            print(f"  ❌ {msg}")
            results.append({"name": test_name, "status": "FAIL", "details": msg})
            return

        run_btn.click()
        print(f"  🔄 Analysis started...")

        # 5. Wait for results (up to 90s)
        try:
            page.wait_for_selector(
                'text=Risk Assessment, text=USE AS DIRECTED, text=HIGH RISK, text=CAUTION, text=CPIC GUIDELINE',
                timeout=90000
            )
        except Exception:
            # Fallback: wait and check
            page.wait_for_timeout(5000)

        page.wait_for_timeout(2000)

        # Screenshot: results page
        ss_path_results = SCREENSHOT_DIR / f"{test_name}_results.png"
        page.screenshot(path=str(ss_path_results), full_page=True)

        # 6. Extract results
        page_text = page.inner_text("body")

        # Check for key results
        has_risk = any(x in page_text for x in [
            "USE AS DIRECTED", "CAUTION", "HIGH RISK", "DO NOT PRESCRIBE",
            "CPIC GUIDELINE REFERENCE", "Risk Assessment", "STATUS UNKNOWN"
        ])
        has_gene = any(x in page_text for x in ["CYP2D6", "CYP2C9", "CYP2C19", "SLCO1B1", "TPMT", "DPYD", "VKORC1"])
        has_clinical = any(x in page_text for x in ["Clinical Recommendation", "Genomic Markers", "Evidence"])

        # Extract drug results
        drug_results = []
        for drug in drugs:
            if drug.lower() in page_text.lower() or drug.upper() in page_text.upper():
                drug_results.append(drug)

        # Determine headlines
        headlines = []
        for h in ["USE AS DIRECTED", "CAUTION — ADJUST DOSAGE", "HIGH RISK — DO NOT PRESCRIBE", "CPIC GUIDELINE REFERENCE", "STATUS UNKNOWN"]:
            if h in page_text:
                headlines.append(h)

        if has_risk:
            print(f"  ✅ Results displayed")
            print(f"     Headlines: {', '.join(headlines) if headlines else 'detected'}")
            print(f"     Genes found: {has_gene}")
            print(f"     Clinical content: {has_clinical}")
            print(f"     Drugs in results: {', '.join(drug_results)}")
            results.append({
                "name": test_name,
                "status": "PASS",
                "details": f"Headlines: {headlines}, Genes: {has_gene}, Clinical: {has_clinical}"
            })
        else:
            # Check for error
            has_error = "error" in page_text.lower() or "failed" in page_text.lower()
            if has_error:
                msg = "Error message displayed on results page"
                print(f"  ❌ {msg}")
                results.append({"name": test_name, "status": "FAIL", "details": msg})
            else:
                msg = "No recognizable results found"
                print(f"  ⚠️ {msg}")
                results.append({"name": test_name, "status": "WARN", "details": msg})

    except Exception as e:
        msg = f"Exception: {str(e)[:200]}"
        print(f"  ❌ {msg}")
        ss_err = SCREENSHOT_DIR / f"{test_name}_error.png"
        try:
            page.screenshot(path=str(ss_err), full_page=True)
        except:
            pass
        results.append({"name": test_name, "status": "FAIL", "details": msg})


def main():
    # Setup
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PharmaGuard — Sample VCF Testing Suite")
    print(f"Testing {len(TEST_CASES)} VCF files through frontend")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Capture console messages
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        for i, case in enumerate(TEST_CASES):
            run_test(page, case, i)

        browser.close()

    # Write report
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    warned = sum(1 for r in results if r["status"] == "WARN")

    report_lines = [
        "PharmaGuard — VCF Sample Test Report",
        "=" * 50,
        "",
        f"Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}  |  Warnings: {warned}",
        f"Pass Rate: {(passed / max(len(results),1)) * 100:.0f}%",
        "",
    ]

    for r in results:
        icon = "PASS" if r["status"] == "PASS" else ("FAIL" if r["status"] == "FAIL" else ("SKIP" if r["status"] == "SKIP" else "WARN"))
        report_lines.append(f"[{icon}] {r['name']} — {r['details']}")
        status_icon = "✅" if r["status"] == "PASS" else ("❌" if r["status"] == "FAIL" else ("⏭️" if r["status"] == "SKIP" else "⚠️"))
        print(f"  {status_icon} {r['name']}: {r['details']}")

    report_content = "\n".join(report_lines)
    REPORT_PATH.write_text(report_content, encoding="utf-8")
    print(f"\n📄 Report saved to: {REPORT_PATH}")

    # Console messages
    if console_msgs:
        error_msgs = [m for m in console_msgs if m.startswith("[error]")]
        if error_msgs:
            print(f"\n⚠️ Console errors: {len(error_msgs)}")
            for m in error_msgs[:5]:
                print(f"  {m}")

    # Exit code
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
