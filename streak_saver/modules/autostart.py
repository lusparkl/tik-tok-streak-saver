import autostarter
import typer
import shutil
from streak_saver.modules.utils import send_error_message, send_success_message, send_script_message

app = typer.Typer()

@app.command("autostart_on")
def enable_autostart():
    """Enable autostart"""
    path = shutil.which("streak-saver")

    if path:
        autostarter.add(path, arguments="send_messages --headless", identifier="streak_saver")
        send_success_message("Autostart enabled🚀")
    else:
        send_error_message("Can't find script path, try to setup and try again.")

@app.command("autostart_off")
def disable_autostart():
    """Disable autostart"""
    autostarter.remove(identifier="streak_saver")
    send_script_message("Disabled autostart⛔")
