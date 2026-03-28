#!/usr/bin/env python3
"""Capture a screenshot of wdf_banner_v3.html - cropped to banner only, high res."""
from pathlib import Path
from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).parent
HTML_FILE = SCRIPT_DIR / "wdf_banner_v3.html"
OUTPUT_PNG = SCRIPT_DIR / "wdf_banner_v3_preview.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1400, 'height': 800}, device_scale_factor=2)
    page.goto(f'file://{HTML_FILE.absolute()}')
    page.wait_for_timeout(500)
    # Crop to banner-wrap element only
    banner = page.locator('.banner-wrap')
    banner.screenshot(path=str(OUTPUT_PNG), type='png')
    browser.close()

print(f"Screenshot saved: {OUTPUT_PNG.name}")
