from streak_saver.modules.send_messages import app as send_messages_app
from streak_saver.modules.get_cookies import app as cookies_app
from streak_saver.modules.autostart import app as autostart_app
from streak_saver.modules.manage_users import app as users_app
from streak_saver.modules.setup import app as setup_app
from playwright.sync_api import sync_playwright
import typer
import json



app = typer.Typer()
app.add_typer(setup_app)
app.add_typer(cookies_app)
app.add_typer(users_app)
app.add_typer(autostart_app)
app.add_typer(send_messages_app)

if __name__ == "__main__":
    app()