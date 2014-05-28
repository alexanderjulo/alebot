Configuration
=============

All the bot configuration is handled in one json-formatted (and thus human-readable) file: `config.json`. Usually alebot will try to find the file in your current working directory.

The following options are available:

nick
    The nickname the bot will use (default: alebot).

ident
    The ident of the bot. In IRC this will be visible as the part between ! and @ (default: alebot).

realname
    The realname of the bot. Can be seen when doing a ``/whois`` on a nickname (default: alebot python irc bot. https://github.com/alexex/alebot)

server
    The server to connect to (default: irc.freenode.net).

port
    The port to use when connecting to the server (default: 6667)

logToStdout
    Whether to print the log to stdout (default: true)

logLevel
    Loglevel. Available options are `DEBUG`, `INFO`, `WARN`, `ERROR` (default: `INFO`)

logFormatter
    A string that defines how the log output should be formatted, see `the python logging docs <https://docs.python.org/2/library/logging.html#formatter-objects>`_ for more info (default: %(asctime)s - %(levelname)s - %(message)s).

logFile
    Either `false` or the path to the logfile, if you want to enable file logging. Please note that if you enable file logging but do not disable logging to stdout, both will be used. (default: `false`)
