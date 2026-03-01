from streak_saver.modules.utils import send_error_message, send_script_message, send_success_message
import typer
import subprocess
import sys
from pathlib import Path
import configparser

app = typer.Typer()

@app.command("setup")
def setup():
    """
    Download browsers for playwright library and create config file.
    """
    send_script_message("Installing browser dependencies...")
    subprocess.run([sys.executable, "-m", "playwright", "install"])
    send_success_message("Installed Browsers!")
    
    config = configparser.ConfigParser()
    config["users"] = {}
    config.add_section("SETTINGS")
    config["SETTINGS"]["last_send"] = ""
    app_dir = typer.get_app_dir("streak_saver")
    config_path = Path(app_dir) / "config.ini"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    Path.touch(config_path)

    send_success_message("Now enter usernames(not nicknames!) of people you want to keep save your streak with. When you finish just press enter")
    while True:
        name = input("Enter username: ").strip()
        if name:
            if name in config["users"].keys():
                send_script_message("Already have this one!")
                continue
            else:
                config["users"][name] = "❤️"
                continue
        
        break
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    send_success_message("Finished setup! Now run <streak-saver login> to login to your tik tok account once and then you're ready to go!")