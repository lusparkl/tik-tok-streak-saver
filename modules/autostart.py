import autostarter
import typer
import shutil

app = typer.Typer()

@app.command("on")
def enable_autostart():
    path = shutil.which("streak-saver")

    if path:
        autostarter.add(path, identifier="streak-saver")
        typer.echo("Autostart enabled!")
    else:
        typer.echo("Can't find script path, try to setup and try again.")

@app.command("off")
def disable_autostart():
    autostarter.remove(identifier="streak-saver")
    typer.echo("Disabled autostart!")
