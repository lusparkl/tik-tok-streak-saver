from pathlib import Path
import configparser
import typer
import json
from playwright.sync_api import sync_playwright
from rich.text import Text
from rich import print


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    app_dir = typer.get_app_dir("streak_saver")
    config_path = Path(app_dir) / "config.ini"
    
    try:
        config.read(config_path, encoding='utf-8')
        return config
    except:
        raise FileNotFoundError("Can't find config. Please use <streak-saver setup> to create it.")


def save_config(config: configparser.ConfigParser) -> None:
    app_dir = typer.get_app_dir("streak_saver")
    config_path = Path(app_dir) / "config.ini"
    
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)

def get_cookies():
    app_dir = typer.get_app_dir("streak_saver")
    cookies_path = Path(app_dir) / "cookies.json"

    with open(cookies_path, "r") as cookies_file:
        cookies = json.load(cookies_file)
    
    return cookies

def send_script_message(text: str) -> None:
    message = Text(text, style="bold")
    print(message)

def send_success_message(text: str) -> None:
    message = Text(text, style="bold blue")
    print(message)

def send_error_message(text: str) -> None:
    message = Text(text, style="bold red")
    print(message)