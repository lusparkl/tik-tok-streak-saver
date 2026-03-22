from streak_saver.modules.utils import send_script_message, send_error_message, send_success_message
from playwright.sync_api import sync_playwright
from pathlib import Path
from time import monotonic
import typer
import json


app = typer.Typer()

@app.command("login")
def login():
    """
    Opens tik tok webpage for you to login. After this saves cookies so next logins can be automated. Everything saves on your pc, no worries.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto("https://www.tiktok.com/")
        send_script_message("Log in to TikTok in the opened browser window. Waiting up to 5 minutes for login cookies...")

        deadline_seconds = 300
        start_time = monotonic()
        cookies = []
        while monotonic() - start_time < deadline_seconds:
            cookies = context.cookies()
            has_login_cookie = any(cookie.get("name") in {"sessionid", "sessionid_ss", "sid_tt"} for cookie in cookies)
            if has_login_cookie:
                break
            page.wait_for_timeout(2000)

        app_dir = typer.get_app_dir("streak_saver")
        cookies_path = Path(app_dir) / "cookies.json"
        cookies_path.parent.mkdir(parents=True, exist_ok=True)
        Path.touch(cookies_path)

        if not cookies or not any(cookie.get("name") in {"sessionid", "sessionid_ss", "sid_tt"} for cookie in cookies):
            send_error_message("Couldn't detect a successful login within 5 minutes. Try again and complete login in the opened browser.")
        else:
            with open(cookies_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f)
        browser.close()
        send_success_message("Saved cookies!")