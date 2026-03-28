#!/usr/bin/env python3
"""Capture a screenshot of the first frame of kahoot-hype-screen_v2.html"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
HTML_FILE = Path(__file__).parent / "kahoot-hype-screen_v2.html"
OUTPUT_PNG = Path(__file__).parent / "kahoot_first_frame.png"
WIDTH = 1920
HEIGHT = 1080

def capture_first_frame():
    """Capture the first frame as a screenshot."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': WIDTH, 'height': HEIGHT})
        
        # Navigate to the HTML file
        page.goto(f'file://{HTML_FILE.absolute()}')
        
        # Wait a moment for initial render
        page.wait_for_timeout(100)
        
        # Take screenshot
        page.screenshot(path=str(OUTPUT_PNG), full_page=False)
        
        browser.close()
        
    print(f"✓ Screenshot saved: {OUTPUT_PNG.name}")
    print(f"  Resolution: {WIDTH}x{HEIGHT}")

if __name__ == "__main__":
    capture_first_frame()
