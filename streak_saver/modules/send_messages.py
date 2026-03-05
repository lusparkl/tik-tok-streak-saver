from streak_saver.modules.utils import (
    get_cookies,
    get_config,
    get_user_message,
    save_config,
    send_error_message,
    send_script_message,
    send_success_message,
)
from playwright.sync_api import sync_playwright
from datetime import date
import typer


app = typer.Typer()


@app.command("send_messages")
def send_messages():
    """
    Send messages to all people from the list. With autostart on runs automatically. Runs only once a day.
    """
    try:
        cookies = get_cookies()
    except FileNotFoundError:
        send_error_message("Cookies not found. Please run <streak-saver login> first.")
        return

    try:
        config = get_config()
    except (FileNotFoundError, KeyError):
        send_error_message("Config not found or invalid. Please run <streak-saver setup> first.")
        return

    if not cookies or not config:
        send_error_message("You haven't setup your app yet. Please use <streak-saver setup> and <streak-saver login> to use it")
        return

    if config["SETTINGS"]["last_send"] == str(date.today()):
        send_script_message("Already send messages today.")
        return

    if not config["users"]:
        send_error_message("There is no one to send messages. Add users with <streak-saver add_user USERNAME>")
        return

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.context.add_cookies(cookies)
            page.wait_for_timeout(2000)
            page.goto("https://www.tiktok.com/messages")
            page.wait_for_timeout(500)

            for username in config["users"].keys():
                page.wait_for_timeout(2000)
                try:
                    page.locator("span").get_by_text(username).first.click()
                    page.get_by_label("Send a message...", exact=True).first.fill(
                        get_user_message(config["users"][username]),
                        timeout=10000,
                    )
                    page.wait_for_timeout(500)
                    page.locator('[data-e2e="message-send"]').click()
                    send_script_message(f"Sent message to the {username}")
                except Exception:
                    send_error_message(f"Something happened while trying to send message to the {username}. Recheck nickname please.")

            config["SETTINGS"]["last_send"] = str(date.today())
            save_config(config)
            send_success_message("Sending complete.")
    except Exception as exc:
        send_error_message(f"Failed to send messages: {exc}")
