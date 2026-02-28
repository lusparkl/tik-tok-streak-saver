import typer
import json
from playwright.sync_api import sync_playwright
import subprocess
import sys
from pathlib import Path
import configparser

app = typer.Typer()

@app.command("setup")
def setup():
    typer.echo("Installing browser dependencies...")
    subprocess.run([sys.executable, "-m", "playwright", "install"])
    typer.echo("Installed Browsers!")
    
    config = configparser.ConfigParser()
    config["users"] = {}
    app_dir = typer.get_app_dir("streak-saver")
    config_path = Path(app_dir) / "config.ini"

    typer.echo("Now enter usernames(not nicknames!) of people you want to keep save your streak with. When you finish just press enter")
    while True:
        name = input("Enter username: ").strip()
        if name:
            if name in config["users"].keys():
                typer.echo("Already have this one!")
                continue
            else:
                config["users"][name] = "❤️"
                continue
        
        break
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    typer.echo("Finished setup! Now run <streak-saver login> to login to your tik tok account once and then you're ready to go!")