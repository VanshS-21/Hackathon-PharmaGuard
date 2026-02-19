"""
PharmaGuard — Reconnaissance Script
Discovers page elements and takes a screenshot of the landing page.
"""
from playwright.sync_api import sync_playwright
import os

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    # Navigate and wait
    page.goto("http://localhost:3000")
    page.wait_for_load_state("networkidle")

    # Take landing page screenshot
    page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing.png"), full_page=True)
    print("Screenshot saved: 01_landing.png")

    # Discover buttons
    buttons = page.locator("button").all()
    print(f"\nFound {len(buttons)} buttons:")
    for i, btn in enumerate(buttons):
        text = btn.inner_text().strip() if btn.is_visible() else "[hidden]"
        enabled = btn.is_enabled()
        print(f"  [{i}] '{text}' visible={btn.is_visible()} enabled={enabled}")

    # Discover links
    links = page.locator("a[href]").all()
    print(f"\nFound {len(links)} links:")
    for link in links[:10]:
        text = link.inner_text().strip()
        href = link.get_attribute("href")
        print(f"  - '{text}' -> {href}")

    # Discover inputs
    inputs = page.locator("input, textarea, select").all()
    print(f"\nFound {len(inputs)} input fields:")
    for inp in inputs:
        name = inp.get_attribute("name") or inp.get_attribute("id") or "[unnamed]"
        itype = inp.get_attribute("type") or "text"
        print(f"  - {name} ({itype})")

    # Discover headings
    headings = page.locator("h1, h2, h3").all()
    print(f"\nFound {len(headings)} headings:")
    for h in headings:
        tag = h.evaluate("el => el.tagName")
        text = h.inner_text().strip()[:80]
        print(f"  <{tag}> {text}")

    # Check for drop zone elements
    dropzones = page.locator("[class*='drop'], [class*='drag'], [class*='upload']").all()
    print(f"\nFound {len(dropzones)} drop/upload zones")

    # Check for drug selection elements
    drug_buttons = page.locator("text=CODEINE").all()
    print(f"\nFound {len(drug_buttons)} elements matching 'CODEINE'")

    browser.close()
    print("\n✅ Reconnaissance complete!")
