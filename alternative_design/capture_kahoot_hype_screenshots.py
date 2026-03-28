#!/usr/bin/env python3
"""Capture Kahoot Hype Screen via lossless screenshots stitched into a GIF.
10-second deterministic loop at 50 FPS, 1920x1080 (16:9).
"""
import subprocess, os, sys, glob, shutil

# ── CONFIG ──────────────────────────────────────────────────────
WIDTH = 1920
HEIGHT = 1080
FPS = 50
LOOP_DUR = 3.0  # 3 second loop (matches HTML LOOP_DURATION)
TOTAL_FRAMES = int(FPS * LOOP_DUR)  # 150 frames
FRAME_INTERVAL_MS = int(1000 / FPS)  # 20ms per frame
WARMUP_MS = 2000  # Let page load and settle
# ────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(SCRIPT_DIR, "kahoot-hype-screen_v2.html")
OUTPUT_GIF = os.path.join(SCRIPT_DIR, "kahoot_hype_screen.gif")
FRAME_DIR = "/tmp/wdf_frames_kahoot_hype"

# Clean frame dir
if os.path.exists(FRAME_DIR):
    shutil.rmtree(FRAME_DIR)
os.makedirs(FRAME_DIR)

print(f"Capturing {TOTAL_FRAMES} frames at {WIDTH}x{HEIGHT}, {FPS}fps, {LOOP_DUR}s loop...")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
    page.goto(f"file://{HTML_PATH}")
    page.wait_for_timeout(WARMUP_MS)

    # Hijack the animation: stop rAF loop, pause CSS animations, expose manual frame control
    page.evaluate("""
    () => {
        // 1. Stop the rAF draw loop
        window._stopped = false;
        const origRAF = window.requestAnimationFrame;
        window.requestAnimationFrame = (cb) => {
            if (!window._stopped) return origRAF(cb);
        };
        window._stopped = true;

        // 2. Pause ALL CSS animations globally
        const allAnims = document.getAnimations();
        allAnims.forEach(a => a.pause());
        window._cssAnims = allAnims;

        // 3. Store the original draw function and startTime
        window._originalDraw = window.draw;
        window._baseTs = performance.now();

        // 4. Expose function to render a precise frame
        window.drawAtTime = (elapsedMs) => {
            // Seek all CSS animations to the correct time
            window._cssAnims.forEach(a => {
                if (a.effect && a.effect.getTiming) {
                    const dur = a.effect.getTiming().duration;
                    if (dur && dur !== 'auto') {
                        // Set currentTime modulo duration for looping anims
                        a.currentTime = elapsedMs % dur;
                    }
                }
            });

            // Update startTime for deterministic canvas rendering
            window.startTime = window._baseTs;
            
            // Call the draw function with the exact timestamp
            const fakeTs = window._baseTs + elapsedMs;
            if (window._originalDraw) {
                window._originalDraw(fakeTs);
            }
            
            // Also trigger updateDiamonds if it exists
            if (window.updateDiamonds) {
                window.updateDiamonds(fakeTs);
            }
        };
    }
    """)

    for i in range(TOTAL_FRAMES):
        elapsed_ms = (i / TOTAL_FRAMES) * LOOP_DUR * 1000
        page.evaluate(f"window.drawAtTime({elapsed_ms})")
        path = os.path.join(FRAME_DIR, f"frame_{i:04d}.png")
        page.screenshot(path=path, type="png")
        if (i + 1) % 50 == 0 or i == TOTAL_FRAMES - 1:
            print(f"  Frame {i + 1}/{TOTAL_FRAMES}")

    page.close()
    browser.close()

print(f"All {TOTAL_FRAMES} frames captured. Generating GIF...")

palette = "/tmp/wdf_palette_kahoot_hype.png"

# Generate palette from all frames
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", os.path.join(FRAME_DIR, "frame_%04d.png"),
    "-vf", f"palettegen=max_colors=256:stats_mode=diff",
    palette
], check=True, capture_output=True)

# Encode GIF
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", os.path.join(FRAME_DIR, "frame_%04d.png"),
    "-i", palette,
    "-lavfi", f"[0:v][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
    OUTPUT_GIF
], check=True, capture_output=True)

gif_size = os.path.getsize(OUTPUT_GIF) / (1024 * 1024)
print(f"\nGIF created: {OUTPUT_GIF}")
print(f"Size: {gif_size:.1f} MB")
print(f"Dimensions: {WIDTH}x{HEIGHT}")
print(f"Framerate: {FPS}fps, Loop: {LOOP_DUR}s, Frames: {TOTAL_FRAMES}")
