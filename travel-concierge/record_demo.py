import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

APP_URL = "https://travel-concierge-frontend-514886372165.us-central1.run.app"
RAW_VIDEO_DIR = "raw_videos"

async def record_demo():
    os.makedirs(RAW_VIDEO_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=RAW_VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        print("Navigating to Travel Concierge App...")
        await page.goto(APP_URL, wait_until="networkidle")
        await asyncio.sleep(2)

        # 1. First prompt: Click prompt chip or type first question
        print("Sending Prompt 1: Recommended destinations in Japan...")
        japan_chip = page.locator(".chip:has-text('Japan Destinations')")
        if await japan_chip.count() > 0:
            await japan_chip.click()
        else:
            await page.fill("#input", "Recommend destinations in Japan")
            await page.click("#form button")

        # Wait for agent response to appear
        await asyncio.sleep(8)

        # 2. Second richer prompt: Weather lookup + Scenic AI Image generation
        print("Sending Prompt 2: Weather in Paris & Scenic Image of Kyoto...")
        await page.fill("#input", "Check the weather in Paris and generate a scenic image of Kyoto")
        await page.click("#form button")

        # Wait for tool calls, weather result, and image generation
        await asyncio.sleep(14)

        print("Closing browser context to finalize raw video...")
        await context.close()
        await browser.close()

        # Get recorded video file path
        recorded_files = [os.path.join(RAW_VIDEO_DIR, f) for f in os.listdir(RAW_VIDEO_DIR) if f.endswith(".webm")]
        if not recorded_files:
            raise Exception("No recorded webm video file found.")
        
        raw_video_path = recorded_files[0]
        print(f"Raw recorded video saved to {raw_video_path}")

        # Mix video with lofi_music.wav using ffmpeg
        output_mp4 = "travel_concierge_demo.mp4"
        print("Mixing raw video with upbeat lofi background music using ffmpeg...")
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-i", "lofi_music.wav",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-filter_complex", "[1:a]volume=0.45[a]",
            "-map", "0:v",
            "-map", "[a]",
            output_mp4
        ]
        subprocess.run(cmd, check=True)
        print(f"Successfully generated final demo video: {output_mp4}")

        # Copy final demo video to artifact directory
        artifact_dir = "/config/.gemini/antigravity/brain/85c4a907-8b22-4544-bcd9-8528aeb2bfe2"
        if os.path.exists(artifact_dir):
            target_artifact = os.path.join(artifact_dir, "travel_concierge_demo.mp4")
            subprocess.run(["cp", output_mp4, target_artifact], check=True)
            print(f"Copied final demo video to artifact: {target_artifact}")

if __name__ == "__main__":
    asyncio.run(record_demo())
