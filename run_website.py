import typer
import json
from playwright.sync_api import sync_playwright
from pathlib import Path
from streak_saver.modules.utils import get_cookies, get_config, send_error_message, send_script_message, send_success_message
from datetime import date


app = typer.Typer()

@app.command("send_messages")
def send_messages():
    cookies = get_cookies()
    config = get_config()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.wait_for_timeout(2000)
        page.goto("https://www.tiktok.com/messages")
        page.wait_for_timeout(500)

        for username in config["users"].keys():
            page.wait_for_timeout(2000)
            page.locator("span").get_by_text(username, exact=True).first.click()




send_messages()