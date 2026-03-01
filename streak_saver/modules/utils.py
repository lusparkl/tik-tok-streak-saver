from pathlib import Path
import configparser
import typer

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