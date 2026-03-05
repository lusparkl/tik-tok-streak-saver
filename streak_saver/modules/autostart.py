from streak_saver.modules.utils import send_error_message, send_script_message, send_success_message
from pyautostart import SmartAutostart
from pathlib import Path
import platform
import typer
import shutil
import os
import sys

app = typer.Typer()


def _get_windows_startup_file(name: str) -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA is not set.")

    return Path(appdata) / "Microsoft/Windows/Start Menu/Programs/Startup" / f"{name}.bat"


def _enable_windows_startup(name: str) -> Path:
    startup_file = _get_windows_startup_file(name)
    startup_file.parent.mkdir(parents=True, exist_ok=True)

    app_dir = Path(typer.get_app_dir("streak_saver"))
    app_dir.mkdir(parents=True, exist_ok=True)
    log_path = app_dir / "autostart.log"

    python_executable = Path(sys.executable)
    command = (
        f"\"{python_executable}\" -m streak_saver.main send_messages "
        f">> \"{log_path}\" 2>&1"
    )
    startup_file.write_text("@echo off\nsetlocal\n" + command + "\n", encoding="utf-8")
    return log_path


def _disable_windows_startup(name: str) -> bool:
    startup_file = _get_windows_startup_file(name)
    if startup_file.exists():
        startup_file.unlink()
        return True
    return False


@app.command("autostart")
def autostart(
    on: bool = typer.Option(None, "--on", help="Enable autostart"),
    off: bool = typer.Option(None, "--off", help="Disable autostart"),
):
    """Manage autostart"""

    if bool(on) == bool(off):
        send_error_message("Use exactly one flag: --on or --off.")
        raise typer.Exit(code=1)

    startup_name = "ss_autostart"
    is_windows = platform.system() == "Windows"

    if on:
        if is_windows:
            try:
                log_path = _enable_windows_startup(startup_name)
            except Exception as exc:
                send_error_message(f"Failed to enable autostart: {exc}")
                raise typer.Exit(code=1)
            send_success_message("Autostart is on🚀")
            send_script_message(f"Autostart log path: {log_path}")
            return

        path = shutil.which("streak-saver")
        if not path:
            send_error_message("Can't find script path, try to setup and try again.")
            raise typer.Exit(code=1)

        autostart_service = SmartAutostart()
        autostart_service.enable(name=startup_name, options={"args": [path]})
        send_success_message("Autostart is on🚀")
        return

    if is_windows:
        if _disable_windows_startup(startup_name):
            send_success_message("Disabled autostart⛔")
        else:
            send_script_message("Autostart was already disabled.")
        return

    autostart_service = SmartAutostart()
    try:
        autostart_service.disable(name=startup_name)
        send_success_message("Disabled autostart⛔")
    except FileNotFoundError:
        send_script_message("Autostart was already disabled.")
