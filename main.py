import typer
import json
from playwright.sync_api import sync_playwright
from modules.get_cookies import app as cookies_app
from modules.setup import app as setup_app
from modules.manage_users import app as users_app
from modules.autostart import app as autostart_app


app = typer.Typer()
app.add_typer(cookies_app)
app.add_typer(setup_app)
app.add_typer(users_app)
app.add_typer(autostart_app, "autostart")

if __name__ == "__main__":
    app()