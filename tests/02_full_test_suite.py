"""
PharmaGuard — Comprehensive Playwright Test Suite
Tests: Landing page, file upload, drug selection, E2E analysis flow, error handling
"""
from playwright.sync_api import sync_playwright
import os
import sys
import time

BASE_URL = "http://localhost:3000"
VCF_FILE = os.path.join(os.path.dirname(__file__), "..", "sample", "sample_patient.vcf")
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Collect console logs
console_logs = []
test_results = []

def log_result(name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    msg = f"{status} | {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    test_results.append({"name": name, "passed": passed, "detail": detail})

def screenshot(page, name):
    path = os.path.join(SCREENSHOTS_DIR, name)
    page.screenshot(path=path, full_page=True)
    print(f"  📸 Screenshot: {name}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    # Capture console messages
    def on_console(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")
    page.on("console", on_console)

    # ================================================================
    # TEST 1: Landing Page Rendering
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 1: Landing Page Rendering")
    print("=" * 60)

    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    screenshot(page, "02_landing_full.png")

    # Check hero heading exists
    h1 = page.locator("h1")
    h1_text = h1.inner_text()
    log_result("H1 heading present", "Precision Medicine" in h1_text, h1_text.replace("\n", " "))

    # Check subtitle text
    subtitle = page.locator("text=Clinical Decision Support System")
    log_result("Subtitle badge visible", subtitle.is_visible())

    # Check compliance badges
    hipaa = page.locator("text=HIPAA Compliant")
    log_result("HIPAA badge visible", hipaa.is_visible())

    local = page.locator("text=Local Processing")
    log_result("Local Processing badge visible", local.is_visible())

    # Check new analysis card
    card_title = page.locator("text=New Analysis Request")
    log_result("Analysis card visible", card_title.is_visible())

    # Check file upload zone
    upload_zone = page.locator("text=Drop VCF file here")
    log_result("Upload zone visible", upload_zone.is_visible())

    # Check drug buttons exist
    drug_names = ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"]
    for drug in drug_names:
        btn = page.locator(f"button:has-text('{drug}')")
        log_result(f"Drug button '{drug}' visible", btn.is_visible())

    # Check Run Analysis button is disabled initially
    run_btn = page.locator("button:has-text('Run Analysis')")
    log_result("Run Analysis button visible", run_btn.is_visible())
    log_result("Run Analysis button disabled (no file/drug)", not run_btn.is_enabled())

    # Check CPIC search box
    search = page.locator("input[placeholder*='CPIC']")
    log_result("CPIC drug search box visible", search.count() > 0 and search.is_visible())

    # ================================================================
    # TEST 2: File Upload Flow
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 2: File Upload Flow")
    print("=" * 60)

    # Upload VCF file via hidden input
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(VCF_FILE)
    page.wait_for_timeout(1000)
    screenshot(page, "03_file_uploaded.png")

    # Verify file name appears
    file_text = page.locator("text=sample_patient.vcf")
    log_result("Uploaded file name displayed", file_text.is_visible())

    # Verify file size appears
    file_size = page.locator("text=KB")
    log_result("File size shown", file_size.is_visible())

    # Verify Remove button appears
    remove_btn = page.locator("text=Remove")
    log_result("Remove button visible after upload", remove_btn.is_visible())

    # Run Analysis should still be disabled (no drug selected)
    run_btn = page.locator("button:has-text('Run Analysis')")
    log_result("Run Analysis still disabled (no drug)", not run_btn.is_enabled())

    # ================================================================
    # TEST 3: Drug Selection & Toggle
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 3: Drug Selection & Toggle")
    print("=" * 60)

    # Select CODEINE
    codeine_btn = page.locator("button:has-text('CODEINE')")
    codeine_btn.click()
    page.wait_for_timeout(500)
    screenshot(page, "04_codeine_selected.png")

    # Run Analysis should now be enabled
    run_btn = page.locator("button:has-text('Run Analysis')")
    log_result("Run Analysis enabled after file + drug", run_btn.is_enabled())

    # Select WARFARIN too
    warfarin_btn = page.locator("button:has-text('WARFARIN')")
    warfarin_btn.click()
    page.wait_for_timeout(300)

    # Toggle WARFARIN off
    warfarin_btn.click()
    page.wait_for_timeout(300)
    screenshot(page, "05_drug_toggled.png")

    # Run Analysis should still be enabled (CODEINE selected)
    log_result("Run Analysis still enabled after toggle", run_btn.is_enabled())

    # ================================================================
    # TEST 4: CPIC Drug Search
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 4: CPIC Drug Search")
    print("=" * 60)

    search_input = page.locator("input[placeholder*='CPIC']")
    if search_input.count() > 0 and search_input.is_visible():
        search_input.fill("ator")
        page.wait_for_timeout(1000)
        screenshot(page, "06_cpic_search.png")

        # Check dropdown appeared
        dropdown = page.locator(".absolute.z-50")
        dropdown_visible = dropdown.count() > 0 and dropdown.first.is_visible()
        log_result("CPIC search dropdown appears", dropdown_visible)

        if dropdown_visible:
            items = dropdown.first.locator("button").all()
            log_result("Search results found", len(items) > 0, f"{len(items)} results")

        # Clear search
        search_input.fill("")
        page.wait_for_timeout(300)
    else:
        log_result("CPIC search box", False, "Not found")

    # ================================================================
    # TEST 5: Error Handling — Remove File
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)

    # Remove the uploaded file
    remove_btn = page.locator("text=Remove")
    if remove_btn.is_visible():
        remove_btn.click()
        page.wait_for_timeout(500)

        # Run Analysis should be disabled again
        run_btn = page.locator("button:has-text('Run Analysis')")
        log_result("Run Analysis disabled after file removal", not run_btn.is_enabled())

        # Upload zone should reappear
        upload_zone = page.locator("text=Drop VCF file here")
        log_result("Upload zone reappears after removal", upload_zone.is_visible())
        screenshot(page, "07_file_removed.png")
    else:
        log_result("Remove button for error test", False, "Not found")

    # ================================================================
    # TEST 6: Full E2E Analysis Flow
    # ================================================================
    print("\n" + "=" * 60)
    print("TEST 6: Full E2E Analysis Flow")
    print("=" * 60)

    # Navigate to fresh page to reset all React state
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)

    # Upload file on fresh page
    file_input = page.locator("input[type='file']")
    file_input.set_input_files(VCF_FILE)
    page.wait_for_timeout(500)

    # Select CODEINE on fresh page
    codeine_btn = page.locator("button:has-text('CODEINE')")
    codeine_btn.click()
    page.wait_for_timeout(300)

    # Click Run Analysis
    run_btn = page.locator("button:has-text('Run Analysis')")
    log_result("Run Analysis button clickable", run_btn.is_enabled())
    screenshot(page, "08_before_submit.png")

    run_btn.click()
    print("  ⏳ Waiting for analysis to complete (up to 60s)...")

    # Wait for processing state or results
    # The app shows a ProcessingState component, then results
    try:
        # Wait for results page to appear (look for "Analysis Results" heading)
        page.wait_for_selector("text=Analysis Results", timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        screenshot(page, "09_results.png")
        log_result("Analysis results page rendered", True)

        # Check result components
        risk_elements = page.locator("text=Risk Assessment").all()
        log_result("Risk assessment section visible", len(risk_elements) > 0 or page.locator("text=ACTIONABLE").count() > 0 or page.locator("text=INFORMATIVE").count() > 0 or page.locator("[class*='risk']").count() > 0)

        # Check for patient ID
        patient_bar = page.locator("text=PATIENT_001")
        log_result("Patient ID displayed in context bar", patient_bar.count() > 0)

        # Check for drug result — look for CODEINE in results
        codeine_result = page.locator("text=CODEINE")
        log_result("CODEINE result displayed", codeine_result.count() > 0)

        # Check for Copy/Download buttons
        copy_btn = page.locator("button:has-text('Copy JSON')")
        log_result("Copy JSON button visible", copy_btn.is_visible())

        download_btn = page.locator("button:has-text('Download JSON')")
        log_result("Download JSON button visible", download_btn.is_visible())

        # Take full-page screenshot of results
        screenshot(page, "10_results_full.png")

        # Check for key clinical components
        # Look for clinical recommendation, action panel content
        action_text = page.locator("text=Clinical Action").all()
        dosing_text = page.locator("text=Dosing").all()
        gene_text = page.locator("text=CYP2D6").all()
        log_result("Clinical content present", len(action_text) > 0 or len(dosing_text) > 0 or len(gene_text) > 0,
                   f"action:{len(action_text)}, dosing:{len(dosing_text)}, gene:{len(gene_text)}")

        # ================================================================
        # TEST 7: Clear Context / New Analysis
        # ================================================================
        print("\n" + "=" * 60)
        print("TEST 7: Clear Context & Reset")
        print("=" * 60)

        # Look for the clear/new analysis button
        clear_btn = page.locator("button:has-text('New Analysis')").first
        if clear_btn.count() > 0 and clear_btn.is_visible():
            clear_btn.click()
            page.wait_for_timeout(1000)
            screenshot(page, "11_reset.png")

            # Should be back to landing
            h1 = page.locator("h1")
            log_result("Reset returns to landing page", "Precision Medicine" in h1.inner_text())
        else:
            # Try alternative clear button
            clear_btns = page.locator("button").all()
            clear_found = False
            for btn in clear_btns:
                text = btn.inner_text().strip().lower()
                if any(word in text for word in ["clear", "new", "reset", "back"]):
                    btn.click()
                    page.wait_for_timeout(1000)
                    clear_found = True
                    break
            if clear_found:
                screenshot(page, "11_reset.png")
                h1 = page.locator("h1")
                log_result("Reset returns to landing page", "Precision Medicine" in h1.inner_text())
            else:
                log_result("Clear/reset button found", False, "No clear button detected")

    except Exception as e:
        screenshot(page, "09_error.png")
        log_result("Analysis results page rendered", False, str(e))

    browser.close()

# ================================================================
# SUMMARY
# ================================================================
print("\n" + "=" * 60)
print("TEST RESULTS SUMMARY")
print("=" * 60)

passed = sum(1 for r in test_results if r["passed"])
failed = sum(1 for r in test_results if not r["passed"])
total = len(test_results)

print(f"\nTotal: {total}  |  Passed: {passed}  |  Failed: {failed}")
print(f"Pass Rate: {passed/total*100:.0f}%\n")

if failed > 0:
    print("FAILED TESTS:")
    for r in test_results:
        if not r["passed"]:
            print(f"  ❌ {r['name']}: {r['detail']}")

print(f"\nConsole logs captured: {len(console_logs)}")
if console_logs:
    print("Last 10 console messages:")
    for log in console_logs[-10:]:
        print(f"  {log}")

# Save report
report_path = os.path.join(SCREENSHOTS_DIR, "..", "test_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("PharmaGuard Playwright Test Report\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total: {total}  |  Passed: {passed}  |  Failed: {failed}\n")
    f.write(f"Pass Rate: {passed/total*100:.0f}%\n\n")
    for r in test_results:
        status = "PASS" if r["passed"] else "FAIL"
        f.write(f"[{status}] {r['name']}")
        if r["detail"]:
            f.write(f" — {r['detail']}")
        f.write("\n")
    f.write(f"\nConsole messages: {len(console_logs)}\n")
    for log in console_logs:
        f.write(f"  {log}\n")

print(f"\n📄 Full report saved to: {report_path}")
