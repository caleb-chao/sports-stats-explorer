"""Optional real-browser smoke test; start Streamlit before running this script."""
import argparse
from pathlib import Path

def main():
    from playwright.sync_api import sync_playwright

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501/NFL_Overview")
    parser.add_argument("--browser-channel", default=None, help="Use chrome or msedge if installed")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel=args.browser_channel, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.get_by_text("NFL season overview", exact=False).wait_for(timeout=60000)
        page.get_by_text("Demo (fictional, offline)", exact=True).click()
        page.get_by_text("DEMO — fictional players, teams, and numbers.", exact=False).wait_for()
        for view in ("Quarterbacks", "Teams", "Injuries"):
            page.get_by_role("combobox").first.click()
            page.get_by_role("option", name=view, exact=True).click()
            frame = page.frame_locator('iframe')
            frame.locator("canvas").wait_for()
            assert frame.locator("canvas").evaluate("el => !!el.getContext('webgl2') || !!el.getContext('webgl')")
            frame.locator("#inspect").select_option("1")
            assert "Demo" in frame.locator("#tip").inner_text()
            frame.get_by_role("button", name="Reset view").click()
            page.get_by_text("Download displayed dataset (CSV)", exact=True).wait_for()
        # The vendored renderer and synthetic data must work without network access.
        page.context.set_offline(True)
        frame.get_by_role("button", name="Reset view").click()
        page.context.set_offline(False)
        page.set_viewport_size({"width": 390, "height": 844})
        assert frame.locator("canvas").is_visible()
        Path("artifacts").mkdir(exist_ok=True)
        page.locator("iframe").screenshot(path="artifacts/nfl-chart.png")
        page.screenshot(path="artifacts/nfl-mobile.png", full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1100})
        page.screenshot(path="artifacts/nfl-demo.png", full_page=True)
        assert not errors, errors
        browser.close()
        print("PASS: three views, WebGL rendering, inspection, reset, responsive layout; screenshots in artifacts/")


if __name__ == "__main__":
    main()
