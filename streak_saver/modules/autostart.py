from streak_saver.modules.utils import send_error_message, send_success_message, send_script_message
import autostarter
import typer
import shutil

app = typer.Typer()

@app.command("autostart")
def autostart(
    on: bool = typer.Option(None, "--on", help="Enable autostart"),
    off: bool = typer.Option(None, "--off", help="Disable autostart")
):
    "Manage autostart"
    if on:
        path = shutil.which("streak-saver")
        if path:
            autostarter.add(path, arguments="send_messages --headless", identifier="streak_saver")
            send_success_message("Autostart enabled🚀")
        else:
            send_error_message("Can't find script path, try to setup and try again.")

    else:
        autostarter.remove(identifier="streak_saver")
        send_success_message("Disabled autostart⛔")





