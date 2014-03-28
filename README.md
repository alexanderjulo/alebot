# alebot

alebot is a lean and super modular python IRC bot with awesome extendability.

## Quickstart
Download this repository, create a `config.json` in the root folder and add as many as you need of the following settings (none required, you are seeing the defaults)[^1]:

```json
{
    "nick": "alebot", // nick
    "ident": "alebot", // ident
    "realname": "alebot python irc bot. https://github/alexex/alebot", // realname
    "server": "irc.freenode.net", // server
    "port": 6667, // port to use
    "channels": [] // list of channels to join
}
```


Then start the bot with `./run.py` or `python run.py`.

All the working plugins in the `plugins` folder will automatically be activated.

## Writing plugins

To find out how to write plugins, check out the the documentation of the `Hook` and `Task` classes (second one is optional) and see the `default.py` plugin that provides basic funtionality like the ping-pong-behavior.

[^1]: actually even creating a config file is optional.
