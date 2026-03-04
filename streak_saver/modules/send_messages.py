from streak_saver.modules.utils import get_cookies, get_config, send_error_message, send_script_message, send_success_message, get_user_message
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import date
import typer
import json



app = typer.Typer()

@app.command("send_messages")
def send_messages():
    """
    Send messages to all people from the list. With autostart on runs automatically. Runs only once a day.
    """
    cookies = get_cookies()
    config = get_config()

    if not cookies or not config:
        send_error_message("You haven't setup your app yet. Please use <streak-saver setup> and <streak-saver login> to use it")
    
    if config["SETTINGS"]["last_send"] == str(date.today()):
        send_script_message("Already send messages today.")
        return
    
    if not config["users"]:
        send_error_message("There is no one to send messages. Add users with <streak-saver add_user USERNAME>")

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = browser.new_page()
        page.context.add_cookies(cookies)
        page.wait_for_timeout(2000)
        page.goto("https://www.tiktok.com/messages")
        page.wait_for_timeout(500)

        for username in config["users"].keys():
            page.wait_for_timeout(2000)
            try:
                page.locator("span").get_by_text(username).first.click()
                page.get_by_label("Send a message...", exact=True).first.fill(get_user_message(config["users"][username]), timeout=10000)
                page.wait_for_timeout(500)
                page.locator('[data-e2e="message-send"]').click()
                send_script_message(f"Sent message to the {username}")
            except:
                send_error_message(f"Something happened while trying to send message to the {username}. Recheck nickname please.")
        
        config["SETTINGS"]["last_send"] == str(date.today())
        send_success_message("Sending complete.")


