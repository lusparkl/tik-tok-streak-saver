from modules.utils import get_config, save_config
import typer

app = typer.Typer()

@app.command("add_user")
def add_user(username: str):
    config = get_config()
    if username in config["users"].keys():
        typer.echo("User is already in your list!")
    else:
        config["users"][username] = "❤️"
        save_config(config)
        typer.echo("Added user!")

@app.command("delete_user")
def delete_user(username: str):
    config = get_config()
    if username not in config["users"].keys():
        typer.echo("Can't find anyone with this username:(")
    else:
        del config["users"][username]
        save_config(config)
        typer.echo("Deleted user!")

@app.command("show_users")
def show_users():
    config = get_config()
    if config["users"]:
        names_str = "There is all your friends: - "
        for name in config["users"].keys():
            names_str += f"{name} -"
        typer.echo(names_str)
    else:
        typer.echo("Your users list is emty, but you can fix that by using <streak-saver add_user USERNAME>!")