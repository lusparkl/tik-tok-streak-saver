from streak_saver.modules.utils import (
    get_cookies,
    get_config,
    get_user_message,
    save_config,
    send_error_message,
    send_script_message,
    send_success_message,
)
from playwright.sync_api import expect, sync_playwright
from datetime import date
import typer


app = typer.Typer()


def _send_message(page, username: str, message: str) -> None:
    # Start from the inbox for each recipient instead of searching the previous
    # conversation's header and message history for a partial username match.
    page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded")
    recipient = page.get_by_text(username, exact=True).filter(visible=True)
    recipient.click(timeout=10000)

    # Prefer the stable attribute, which does not depend on the UI language.
    # Retain the accessible-label selector for layouts using the older editor.
    composer = page.locator('[data-e2e="message-input-area"]').filter(visible=True).or_(
        page.get_by_label("Send a message...", exact=True).filter(visible=True)
    )
    composer.fill(message, timeout=10000)
    page.locator('[data-e2e="message-send"]').filter(visible=True).click(timeout=10000)
    # A click alone is not enough: wait for the UI to consume the draft before
    # navigating away or recording this recipient as sent.
    expect(composer).to_be_empty(timeout=10000)


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

    today = str(date.today())
    if config["SETTINGS"]["last_send"] == today:
        send_script_message("Already send messages today.")
        return

    if not config["users"]:
        send_error_message("There is no one to send messages. Add users with <streak-saver add_user USERNAME>")
        return

    if "sent_dates" not in config:
        config.add_section("sent_dates")
    pending = [
        username for username in config["users"]
        if config["sent_dates"].get(username) != today
    ]
    failed = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                context.add_cookies(cookies)
                page = context.new_page()

                for username in pending:
                    try:
                        _send_message(page, username, get_user_message(config["users"][username]))
                    except Exception as exc:
                        failed.append(username)
                        send_error_message(f"Failed to send message to {username}: {exc}")
                        continue
                    config["sent_dates"][username] = today
                    save_config(config)
                    send_script_message(f"Sent message to {username}")
            finally:
                browser.close()
    except Exception as exc:
        send_error_message(f"Failed to send messages: {exc}")
        raise typer.Exit(code=1) from exc

    if failed:
        send_error_message(
            f"Messages failed for: {', '.join(failed)}. Run send_messages again to retry; "
            "recipients already sent today will be skipped."
        )
        raise typer.Exit(code=1)

    config["SETTINGS"]["last_send"] = today
    save_config(config)
    send_success_message("Sending complete.")
