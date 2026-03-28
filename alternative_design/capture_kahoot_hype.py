#!/usr/bin/env python3
"""
Capture kahoot-hype-screen_v2.html as a seamless looping GIF.
10-second deterministic loop at 50 FPS, 1920x1080 (16:9).
"""
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

# === CONFIGURATION ===
HTML_FILE = Path(__file__).parent / "kahoot-hype-screen_v2.html"
OUTPUT_GIF = Path(__file__).parent / "kahoot_hype_screen.gif"
TEMP_VIDEO = Path(__file__).parent / "kahoot_temp.webm"

WIDTH = 1920
HEIGHT = 1080
FPS = 50
DURATION = 10  # seconds
LOOP_DUR = 10000  # milliseconds (must match HTML LOOP_DURATION)

def capture_video():
    """Capture the animation as a video using Playwright."""
    print(f"Capturing {DURATION}s video at {WIDTH}x{HEIGHT} @ {FPS} FPS...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': WIDTH, 'height': HEIGHT},
            record_video_dir=str(Path(__file__).parent),
            record_video_size={'width': WIDTH, 'height': HEIGHT}
        )
        page = context.new_page()
        
        # Navigate to HTML
        page.goto(f'file://{HTML_FILE.absolute()}')
        
        # Wait for initial render
        page.wait_for_timeout(500)
        
        # Record for the full loop duration
        page.wait_for_timeout(DURATION * 1000)
        
        # Close to finalize video
        context.close()
        browser.close()
    
    # Find the recorded video
    video_files = list(Path(__file__).parent.glob("*.webm"))
    if video_files:
        latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
        latest_video.rename(TEMP_VIDEO)
        print(f"✓ Video captured: {TEMP_VIDEO.name}")
    else:
        raise FileNotFoundError("No video file was created")

def generate_gif():
    """Convert video to optimized GIF using ffmpeg."""
    print(f"Generating GIF at {FPS} FPS...")
    
    # Generate palette for better quality
    palette_file = Path(__file__).parent / "palette.png"
    palette_cmd = [
        'ffmpeg', '-y',
        '-i', str(TEMP_VIDEO),
        '-vf', f'fps={FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos,palettegen=stats_mode=diff',
        str(palette_file)
    ]
    
    print("  Generating palette...")
    subprocess.run(palette_cmd, check=True, capture_output=True)
    
    # Generate GIF with palette
    gif_cmd = [
        'ffmpeg', '-y',
        '-i', str(TEMP_VIDEO),
        '-i', str(palette_file),
        '-filter_complex',
        f'fps={FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle',
        '-loop', '0',
        str(OUTPUT_GIF)
    ]
    
    print("  Encoding GIF...")
    subprocess.run(gif_cmd, check=True, capture_output=True)
    
    # Cleanup
    TEMP_VIDEO.unlink()
    palette_file.unlink()
    
    size_mb = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"✓ GIF created: {OUTPUT_GIF.name} ({size_mb:.1f} MB)")

def main():
    """Main execution."""
    print("=== Kahoot Hype Screen GIF Generator ===\n")
    
    if not HTML_FILE.exists():
        print(f"✗ HTML file not found: {HTML_FILE}")
        return
    
    try:
        capture_video()
        generate_gif()
        print("\n✓ Done!")
        print(f"  Output: {OUTPUT_GIF}")
        print(f"  Resolution: {WIDTH}x{HEIGHT}")
        print(f"  Frame rate: {FPS} FPS")
        print(f"  Duration: {DURATION}s (seamless loop)")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        # Cleanup on error
        if TEMP_VIDEO.exists():
            TEMP_VIDEO.unlink()

if __name__ == "__main__":
    main()
