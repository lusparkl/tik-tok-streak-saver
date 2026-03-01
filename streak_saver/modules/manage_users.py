from streak_saver.modules.utils import get_config, save_config
import typer

app = typer.Typer()

@app.command("add_user")
def add_user(username: str):
    """
    Add user to your users list.

    Add user to your users list to send automatical messages to them. Gives default message "❤️" automatically.

    Attributes:
        username (str): Exact username of the person who you wanna add.
    """
    config = get_config()
    if username in config["users"].keys():
        typer.echo("User is already in your list!")
    else:
        config["users"][username] = "❤️"
        save_config(config)
        typer.echo("Added user!")

@app.command("delete_user")
def delete_user(username: str):
    """
    Delete user from your users list.

    Delete user from your users list to stop sending automatical messages to them.

    Attributes:
        username (str): Exact username of the person who you wanna delete.
    """
    config = get_config()
    if username not in config["users"].keys():
        typer.echo("Can't find anyone with this username:(")
    else:
        del config["users"][username]
        save_config(config)
        typer.echo("Deleted user!")

@app.command("show_users")
def show_users():
    """
    Show list of all your users with their default messages
    """
    config = get_config()
    if config["users"]:
        names_str = "There is all your friends: - "
        for name in config["users"].keys():
            names_str += f"{name}: {config['users'][name]} -"
        typer.echo(names_str)
    else:
        typer.echo("Your users list is emty, but you can fix that by using <streak-saver add_user USERNAME>!")

@app.command("change_default_message")
def change_default_message(new_message: str):
    """
    Change default messages for all users in your list.

    Doesn't affect new users and can rewrite your custom messages for some users.

    Attributes:
        new_message (str): Messages that you want to send automatically.
    """
    config = get_config()
    if config["users"]:
        for username in config["users"].keys():
            config["users"][username] = new_message
        
        typer.echo(f"Successfuly changed default message to the {new_message}.")
    else:
        typer.echo("Your friends list is empty. Use <streak-saver add_user USERNAME> to add them!")

@app.command("change_default_message_for")
def change_default_message_for_user(username: str, new_message: str):
    """
    Change default message for one user from your list.

    Can be rewritten by <change_default_message>.

    Attributes:
        username (str): Exact username of the user.
        new_message (str): Messages that you want to send automatically.
    """
    config = get_config()
    try:
        if config["users"][username]:
            config["users"][username] = new_message
            typer.echo(f"Successfuly changed default message for {username} to {new_message}.")
    except KeyError:
        typer.echo(f"Can't find user with nickname {username}, recheck it and try again.")