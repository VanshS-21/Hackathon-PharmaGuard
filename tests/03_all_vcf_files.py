"""
PharmaGuard — All VCF Files Test
Tests every VCF file in sample/ and test_data/ against the full E2E analysis flow.
For each file: upload → select CODEINE → INITIATE_ANALYSIS → verify results page.
"""
from playwright.sync_api import sync_playwright
import os
import sys
import glob
import time

BASE_URL = "http://localhost:3000"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots", "vcf_all")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Collect all VCF files
vcf_files = sorted(
    glob.glob(os.path.join(ROOT, "sample", "*.vcf")) +
    glob.glob(os.path.join(ROOT, "test_data", "*.vcf"))
)

print(f"Found {len(vcf_files)} VCF file(s) to test:")
for f in vcf_files:
    print(f"  • {os.path.relpath(f, ROOT)}")

results = []

def log(name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    msg = f"{status} | {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    results.append({"name": name, "passed": passed, "detail": detail})

def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, name)
    page.screenshot(path=path, full_page=True)
    print(f"  📸 {name}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    for vcf_path in vcf_files:
        vcf_name = os.path.basename(vcf_path)
        rel = os.path.relpath(vcf_path, ROOT)
        slug = vcf_name.replace(".vcf", "").replace(" ", "_")

        print(f"\n{'=' * 60}")
        print(f"Testing: {rel}")
        print(f"{'=' * 60}")

        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        try:
            # --- Navigate to app ---
            page.goto(BASE_URL)
            page.wait_for_load_state("networkidle")

            # --- Upload VCF file ---
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(vcf_path)
            page.wait_for_timeout(600)

            # Verify filename appears
            fname_el = page.locator(f"text={vcf_name}")
            file_shown = fname_el.count() > 0
            log(f"[{vcf_name}] File name displayed", file_shown)

            # --- Select CODEINE ---
            codeine_btn = page.locator("button:has-text('CODEINE')")
            codeine_btn.click()
            page.wait_for_timeout(300)

            # --- Run Analysis ---
            run_btn = page.locator("button:has-text('INITIATE_ANALYSIS')")
            enabled = run_btn.count() > 0 and run_btn.is_enabled()
            log(f"[{vcf_name}] INITIATE_ANALYSIS enabled", enabled)

            screenshot(page, f"{slug}_01_before.png")

            if not enabled:
                log(f"[{vcf_name}] Analysis completed", False, "Button not enabled — skipping")
                page.close()
                continue

            run_btn.click()
            print(f"  ⏳ Waiting for analysis (up to 60s)…")

            # --- Wait for results or error ---
            try:
                # Could land on results page OR show an error toast
                page.wait_for_selector("text=Analysis Results", timeout=90000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
                screenshot(page, f"{slug}_02_results.png")
                log(f"[{vcf_name}] Results page rendered", True)

                # Check for drug name in results
                drug_el = page.locator("text=CODEINE")
                log(f"[{vcf_name}] CODEINE in results", drug_el.count() > 0)

                # Check for any risk label
                has_risk = (
                    page.locator("text=USE AS DIRECTED").count() > 0
                    or page.locator("text=ADJUST DOSAGE").count() > 0
                    or page.locator("text=CONTRAINDICATED").count() > 0
                    or page.locator("text=GUIDELINE REQ.").count() > 0
                    or page.locator("text=Risk Assessment").count() > 0
                    or page.locator("text=NO_DATA").count() > 0
                    or page.locator("text=no data").count() > 0
                    or page.locator("text=insufficient").count() > 0
                )
                log(f"[{vcf_name}] Risk label/section visible", has_risk)

                # Check patient ID — use two separate checks
                patient_by_class = page.locator("[class*='patient']")
                patient_by_text  = page.locator("text=PATIENT_")
                patient_visible  = patient_by_class.count() > 0 or patient_by_text.count() > 0
                log(f"[{vcf_name}] Patient context bar visible", patient_visible)

                # Check no JS errors
                critical_errors = [e for e in console_errors if "Failed to load resource" not in e]
                log(f"[{vcf_name}] No critical JS errors", len(critical_errors) == 0,
                    f"{len(critical_errors)} errors" if critical_errors else "")

            except Exception as e:
                screenshot(page, f"{slug}_02_error.png")
                log(f"[{vcf_name}] Results page rendered", False, str(e)[:120])

        except Exception as e:
            log(f"[{vcf_name}] Test crashed", False, str(e)[:120])
        finally:
            page.close()

    browser.close()

# ================================================================
# SUMMARY
# ================================================================
print(f"\n{'=' * 60}")
print("ALL VCF FILES — TEST SUMMARY")
print(f"{'=' * 60}")

passed = sum(1 for r in results if r["passed"])
failed = sum(1 for r in results if not r["passed"])
total = len(results)

print(f"\nTotal checks: {total}  |  Passed: {passed}  |  Failed: {failed}")
print(f"Pass Rate: {passed/total*100:.0f}%\n")

if failed > 0:
    print("FAILED CHECKS:")
    for r in results:
        if not r["passed"]:
            print(f"  ❌ {r['name']}: {r['detail']}")

# Save report
report_path = os.path.join(os.path.dirname(__file__), "vcf_all_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("PharmaGuard — All VCF Files Test Report\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total checks: {total}  |  Passed: {passed}  |  Failed: {failed}\n")
    f.write(f"Pass Rate: {passed/total*100:.0f}%\n\n")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        line = f"[{status}] {r['name']}"
        if r["detail"]:
            line += f" — {r['detail']}"
        f.write(line + "\n")

print(f"\n📄 Report saved to: {report_path}")
print(f"📸 Screenshots in: {SCREENSHOTS_DIR}")

sys.exit(0 if failed == 0 else 1)
