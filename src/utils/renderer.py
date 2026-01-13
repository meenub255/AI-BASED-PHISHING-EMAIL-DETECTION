import os
import asyncio
from playwright.async_api import async_playwright

class EmailRenderer:
    def __init__(self, output_dir: str = "data/screenshots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def render_html(self, html_content: str, email_id: str) -> str:
        """Renders HTML content to a PNG image and returns the file path."""
        file_path = os.path.join(self.output_dir, f"{email_id}.png")
        
        async with async_playwright() as p:
            # We use a standard desktop viewport for detection
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 800, 'height': 600})
            
            # Set content and wait for it to load
            await page.set_content(html_content)
            await page.wait_for_load_state("networkidle")
            
            # Take a full-page screenshot to capture the entire layout
            await page.screenshot(path=file_path, full_page=True)
            await browser.close()
            
        print(f"[Renderer] Screenshot saved to: {file_path}")
        return file_path

if __name__ == "__main__":
    # Test rendering
    renderer = EmailRenderer()
    mock_html = """
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h1 style="color: #0070ba;">PayPal</h1>
            <p>Your account has been limited. Please click below to verify.</p>
            <a href="#" style="background: #0070ba; color: white; padding: 10px 20px; text-decoration: none;">Verify Now</a>
        </body>
    </html>
    """
    asyncio.run(renderer.render_html(mock_html, "test_render"))
