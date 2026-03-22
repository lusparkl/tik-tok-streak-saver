# streak saver

## Streak saver is python CLI app thats automatically sends messages to your friends in tik tok to keep streak alive.

I have lot's of friends who really do care about tik tok streak pets and there was thousands of times when I forgot about this streaks and they was angry on me. So I decided to make script that will do it automaticaly for me every time I turn on my pc. You can customize who and what you're sending, so you can create different messages for all of your friends!

## Technologies

* [Typer](https://typer.tiangolo.com/) - to realize CLI functionality.
* [Playwright](https://playwright.dev/python/) - to interact with tik tok via browser.
* [PyAutostart](https://pypi.org/project/pyautostart/) - to start app every time you turn on your pc.
* [Rich](https://rich.readthedocs.io/en/stable/index.html) - to make prints prettier.

---

## How to use

1. Install package by running `pipx install streak-saver`.
2. Run `streak-saver setup` it'll download playwright deps and create config files. You can also add your friends on this step.
3. Run `streak-saver login` you'll find out browser page with tik tok in there, you need to login to your account once to save cookies. Your data will stay on your pc, no worries.
4. Run `streak-saver autostart --on` to turn run script every time you start your pc(to disable it run `autostart --off`).

**Done!** Now you can either forget about it or use some of the commands lower to customize your messages and to add/remove users who you wanna message.

**Warning**: You should run `streak-saver login` from time to time to renew your cookies. Something like once a week will be enough.

---

## Commands

- `setup` - use only after you download package or if package files corrupted. 
- `login` - use to renew cookies/change account. Necessary before first `send_messages`.
- `add_user USERNAME` - add user to your "users list"(people who you'll be messaging). Use username not nickname!
- `delete_user USERNAME` - delete user from your users list.
- `show_users` - show nicknames and messages that you're senging from the users list.
- `change_default_message MESSAGE` - change default message(by default it's ❤️).
- `change_message_for USERNAME MESSAGE` - change message for specific user from your users list.
- `send_messages` - to send messages for all users from your list(with autostart on runs automatically). Runs only once a day.
- `autostart --on/--off` - use to manage autostart
- `streak-saver` - btw it runs `send_messages` command by default, it's for autostart feature
 ## Bugs

 If you found bug, please let me know about it by opening issue in github repository🙏
