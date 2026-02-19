"""
Targeted test: test_data/sample.vcf (CYP2C19 variants) + CODEINE
Verifies the ProcessingState fix — should complete within 60s now.
"""
from playwright.sync_api import sync_playwright
import os

VCF = os.path.join(os.path.dirname(__file__), "..", "test_data", "sample.vcf")
SHOTS = os.path.join(os.path.dirname(__file__), "screenshots", "vcf_all")
BASE_URL = "http://localhost:3000"

os.makedirs(SHOTS, exist_ok=True)

print(f"Testing: {os.path.relpath(VCF)}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    # Upload
    page.locator("input[type='file']").set_input_files(VCF)
    page.wait_for_timeout(500)
    print("File uploaded:", page.locator("text=sample.vcf").count() > 0)

    # Select CODEINE
    page.locator("button:has-text('CODEINE')").click()
    page.wait_for_timeout(300)

    btn = page.locator("button:has-text('INITIATE_ANALYSIS')")
    print("Button enabled:", btn.is_enabled())
    btn.click()
    print("Clicked — waiting up to 60s for Analysis Results...")

    try:
        page.wait_for_selector("text=Analysis Results", timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(SHOTS, "sample_fixed_results.png"), full_page=True)
        print("\n✅ SUCCESS: Results page rendered!")
        print("CODEINE in results:", page.locator("text=CODEINE").count() > 0)
        print("Patient bar visible:", page.locator("text=PATIENT_").count() > 0)
        print("Risk visible:", page.locator("text=Risk Assessment").count() > 0
              or page.locator("text=Unknown").count() > 0)
    except Exception as e:
        page.screenshot(path=os.path.join(SHOTS, "sample_fixed_error.png"), full_page=True)
        print(f"\n❌ FAIL: {e}")

    browser.close()

print("\nDone. Screenshot saved to tests/screenshots/vcf_all/")
