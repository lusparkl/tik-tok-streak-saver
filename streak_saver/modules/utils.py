from rich.text import Text
from pathlib import Path
import configparser
from rich import print
import typer
import json


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    app_dir = typer.get_app_dir("streak_saver")
    config_path = Path(app_dir) / "config.ini"

    if not config_path.exists():
        raise FileNotFoundError("Can't find config. Please use <streak-saver setup> to create it.")

    config.read(config_path, encoding="utf-8")
    if "users" not in config or "SETTINGS" not in config:
        raise KeyError("Config is missing required sections.")
    if "last_send" not in config["SETTINGS"]:
        config["SETTINGS"]["last_send"] = ""
    if "default_message" not in config["SETTINGS"]:
        config["SETTINGS"]["default_message"] = "❤️"

    return config


def save_config(config: configparser.ConfigParser) -> None:
    app_dir = typer.get_app_dir("streak_saver")
    config_path = Path(app_dir) / "config.ini"
    
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)

def get_cookies():
    app_dir = typer.get_app_dir("streak_saver")
    cookies_path = Path(app_dir) / "cookies.json"

    if not cookies_path.exists():
        send_error_message("Can't find cookies. Please use <streak-saver login> first.")

    with open(cookies_path, "r", encoding="utf-8") as cookies_file:
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

def get_user_message(user_message) -> str:
    if not user_message.strip():
        config = get_config()
        return config["SETTINGS"]["default_message"]
    else:
        return user_message
