import autostarter
import typer
import shutil

app = typer.Typer()

@app.command("autostart_on")
def enable_autostart():
    """Enable autostart"""
    path = shutil.which("streak_saver")

    if path:
        autostarter.add(path, identifier="streak_saver")
        typer.echo("Autostart enabled!")
    else:
        typer.echo("Can't find script path, try to setup and try again.")

@app.command("autostart_off")
def disable_autostart():
    """Disable autostart"""
    autostarter.remove(identifier="streak_saver")
    typer.echo("Disabled autostart!")
