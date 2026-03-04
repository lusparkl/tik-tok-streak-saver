from streak_saver.modules.utils import send_error_message, send_success_message, send_script_message
from pyautostart import SmartAutostart
import typer
import shutil

app = typer.Typer()

@app.command("autostart")
def autostart(
    on: bool = typer.Option(None, "--on", help="Enable autostart"),
    off: bool = typer.Option(None, "--off", help="Disable autostart")
):
    """Manage autostart"""

    path = shutil.which("streak-saver")
    autostart = SmartAutostart()
    options = {
        "args": [
            path
        ]
    }
    
    if on:
        if path:
            autostart.enable(name="streak-saver", options=options)
            send_success_message("Autostart is on🚀")
        else:
            send_error_message("Can't find script path, try to setup and try again.")
    else:
        autostart.disable(name="streak-saver")
        send_success_message("Disabled autostart⛔")





