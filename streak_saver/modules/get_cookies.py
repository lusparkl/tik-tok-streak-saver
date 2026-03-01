import typer
import json
from playwright.sync_api import sync_playwright
from pathlib import Path

app = typer.Typer()

@app.command("login")
def login():
    """
    Opens tik tok webpage for you to login. After this saves cookies so next logins can be automated. Everything saves on your pc, no worries.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = browser.new_page()
        
        page.goto("https://www.tiktok.com/")
        page.wait_for_timeout(5000)
        res = input("Press enter to continue(only if you logged in)")
        page.wait_for_timeout(10000)
        
        cookies = page.context.cookies()
        app_dir = typer.get_app_dir("streak_saver")
        cookies_path = Path(app_dir) / "cookies.json"
        cookies_path.parent.mkdir(parents=True, exist_ok=True)
        Path.touch(cookies_path)
        
        if not cookies:
            typer.echo("Something wrong, cookies is empty. Try again please and don't forget to allow cookies!")
        else:
            with open(cookies_path, 'w') as f:
                json.dump(cookies, f)
        browser.close()