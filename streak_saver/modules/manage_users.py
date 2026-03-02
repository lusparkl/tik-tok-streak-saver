from streak_saver.modules.utils import get_config, save_config, send_error_message, send_script_message, send_success_message, get_user_message
import typer

app = typer.Typer()

@app.command("add_user")
def add_user(username: str):
    """
    Add user to your users list.

    Add user to your users list to send automatical messages to them. Uses default message unless you change it.

    Attributes:
        username (str): Exact username of the person who you wanna add.
    """
    config = get_config()
    if username in config["users"].keys():
        send_error_message("User is already in your list.")
    else:
        config["users"][username] = ""
        save_config(config)
        send_success_message(f"Added user {username}.")

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
        send_error_message("Can't find anyone with this username:(")
    else:
        del config["users"][username]
        save_config(config)
        send_success_message("Deleted user.")

@app.command("show_users")
def show_users():
    """
    Show list of all your users with their default messages
    """
    config = get_config()
    if config["users"]:
        names_str = "There is all your friends: - "
        for name in config["users"].keys():
            names_str += f"{name}: {get_user_message(config['users'][name])} - "
        send_script_message(names_str)
    else:
        send_error_message("Your users list is emty, but you can fix that by using <streak-saver add_user USERNAME>.")

@app.command("change_default_message")
def change_default_message(new_message: str):
    """
    Change default messages for all users in your list.

    Attributes:
        new_message (str): Messages that you want to send automatically.
    """
    if new_message.strip():
        config = get_config()
        config["SETTINGS"]["default_message"] = new_message
        send_success_message(f"Changed default message to {new_message}")
        save_config(config)
    else:
        send_error_message("Please provide not empty new message")


@app.command("change_message_for")
def change_message_for_user(username: str, new_message: str):
    """
    Change default message for one user from your list.

    Attributes:
        username (str): Exact username of the user.
        new_message (str): Messages that you want to send automatically.
    """
    config = get_config()
    try:
        if config["users"][username]:
            config["users"][username] = new_message
            save_config(config)
            send_success_message(f"Successfuly changed default message for {username} to {new_message}.")
    except KeyError:
        send_error_message(f"Can't find user with nickname {username}, recheck it and try again.")