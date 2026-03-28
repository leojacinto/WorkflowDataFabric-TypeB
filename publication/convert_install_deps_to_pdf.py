#!/usr/bin/env python3
"""Convert install_lab_dependencies.html to PDF using Playwright."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).parent
HTML_FILE = BASE_DIR / "install_lab_dependencies.html"
OUTPUT_PDF = BASE_DIR / "install_lab_dependencies.pdf"

print(f"Converting HTML to PDF...")
print(f"Input:  {HTML_FILE}")
print(f"Output: {OUTPUT_PDF}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Load the HTML file
    page.goto(f"file://{HTML_FILE}")
    
    # Wait for content to load
    page.wait_for_timeout(2000)
    
    # Generate PDF
    page.pdf(
        path=str(OUTPUT_PDF),
        format='A4',
        margin={
            'top': '2cm',
            'right': '2cm',
            'bottom': '2cm',
            'left': '2cm'
        },
        print_background=True,
        display_header_footer=False,
    )
    
    browser.close()

pdf_size = OUTPUT_PDF.stat().st_size / (1024 * 1024)
print(f"\nPDF created successfully!")
print(f"Location: {OUTPUT_PDF}")
print(f"Size: {pdf_size:.1f} MB")
