from asynchat import async_chat
import asyncore
import socket
import fnmatch
import json
import imp
import pkgutil


class Alebot(async_chat):

    """
        The main bot class, where all the magic happens.

        This class handles the socket and all incoming and outgoing
        data. This classes methods should be used for sending data.

        It supplies a hook function with which plugins can register
        their hooks to be notified if fitting data can be received.

        Please check out :class:`Hook` and :func:`hook` to find out
        how hooking your plugins in works.

        Please note that this bot does absolutely nothing by itself.

        It won't even answer pings or identify. But there are some
        system plugins to do that. Check the plugins folder.

            .. attribute:: config

                Holds the bot configuration.
    """

    Hooks = []

    def __init__(self):
        """
            Initiates the parent and some necessary variables.

            Then reads the configuration, finds all the plugins and their
            hooks and instantiates them.
        """
        # system crap
        async_chat.__init__(self)
        self.set_terminator('\r\n')
        self.buffer = ''

        # load the default config
        self.config = {
            'nick': 'alebot',
            'ident': 'alebot',
            'realname': 'alebot python irc bot. https://github/alexex/alebot',
            'server': 'irc.freenode.net',
            'port': 6667
        }

        # load an eventual configuration
        self.load_config()

        # load plugins and their hooks
        self.load_hooks()

        # activate them
        self.activate_hooks()

    @classmethod
    def hook(cls, Hook):
        """
            This method will register a hook with the bot. It is
            supposed to be used as a decorator, but can also be used
            as a normal function. Please see the :class:`Hook` class
            documentation for an overview what a hook should look like.

            This method will save the :class:`Hook` class with the
            :class:`Bot` class until the :func:`__init__` function
            instantiates the hooks.
        """
        cls.Hooks.append(Hook)

    def load_hooks(self):
        """
            Will load all the hooks from the plugin folder. It will
            only load them though! The plugins still have to register
            themselves with the :func:`hook` function.

            This function does not do anything yet. Plugins have to be
            in the the same file as the bot itself.
        """
        for _, name, _ in pkgutil.iter_modules(['plugins']):
            fid, pathname, desc = imp.find_module(name, ['plugins'])
            try:
                imp.load_module(name, fid, pathname, desc)
                print("Loaded plugin '%s'" % pathname)
            except Exception as e:
                print("Could not load plugins '%s': %s"
                        % (pathname, e))
            if fid:
                fid.close()

    def activate_hooks(self):
        """
            Will instantiate all the loaded hooks.
        """
        self.hooks = []
        for Hook in Alebot.Hooks:
            self.hooks.append(Hook(self))

    def call_hooks(self, event):
        """
            Will check through all instantiated plugins and call the
            ones that match the given event.
        """
        for hook in self.hooks:
            if hook.match(event):
                hook.call(event)

    def load_config(self):
        """
            Will open the local config file `config.json` and load
            it as json. Will only accept a json object.

            There are no required values. The file itself it optional.
            The bot will supply default values, if there are none
            specified.

            Alebot itself makes use of the following options:

                `nick`
                `ident`
                `realname`
                `server`
                `port`

            Any additional option can be configured. Plugin developers
            are encouraged to specifiy plugin objects with own
            configuration, as long as they make sure to use a specific
            name to avoid conflicts.
        """
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            f.close()
            self.config = dict(self.config.items() + config.items())
            print("Configuration loaded.")
        except Exception as e:
            print("No configuration loaded: %s" % e)

    def connect(self):
        """
            Creates a socket and kicks off the connection process.
        """
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        async_chat.connect(self, (self.config['server'], self.config['port']))
        asyncore.loop()

    def handle_connect(self):
        """
            As soon as the socket is connected, the (made up) event
            `SOCK_CONNECTED` will be called! Use it to identify
            yourself. This bot does NOTHING by itself.
        """
        event = Event('SOCK_CONNECTED')
        self.call_hooks(event)

    def send_raw(self, data):
        """
            Sends raw commands to the server. Only adds CLRF as a suffix.

                :param data: the IRC command and body to send, fully
                formatted as such.
        """
        self.push('%s\r\n' % data)

    def collect_incoming_data(self, data):
        """
            Collects the incoming data and adds it to the buffer.

                :param data: The received data from the server.

            **Please do not use this function manually! It is only
            to be used by asnchat!**
        """
        self.buffer += data

    def found_terminator(self):
        """
            As IRC is a line based protocol which means every command
            is in its own line, this function is called as soon as a
            line and thus a command has been completely received.

            The line is read from the buffer and the buffer cleared.

            The function only does very basic syntax correction, to
            clear up input that does not match the usual format.

            I.e. a PING command does not follow the usual syntax.

            Thusly the function will get the relevant parameter and
            fill it into the usual structure.

            This function will call the func:`call_hooks` function with
            the extracted data.
        """

        line = self.buffer
        self.buffer = ''

        line = line.split(' ', 3)

        event = Event()

        if (line[0][0] == ':'):

            event.user = line[0][1:]
            event.name = line[1]
            event.target = line[2]

            if (line[1] != 'JOIN'):
                event.body = line[3][1:]

        elif (line[0] == 'PING'):
            event.name = line[0]
            event.body = line[1][1:]

        self.call_hooks(event)


class Event(object):

    """
        The :class:`Event` class is used to store data about the
        event and provide some helper methods that should save you
        some string manipulation.

        .. attribute:: name

            The name attribute should always be given and will be a
            `string`, either as defined in the IRC RFC (event number
            or command) or one of the following custom events:

                `SOCK_CONNECTED`: Sent as soon as the socket is
                connected.

        Depending on the type of the event there might be one or me of
        the following attributes not empty (not `None`):

        .. attribute:: user

            The user that caused the event. In case it is a channel or
            private message, it is the sender of the message, in case
            of a join, the joining person, in case of a kick, the
            kicking person and so on. If this is an actual user, and
            not a server, :attr:`nick`, :attr:`ident` and :attr`host`
            should be available, too.

            If this is a user, it will be in the format of:

                `nick!ident@host`

            If it is a server, it will be in the form of:

                `subdomain.domain.zone`

        .. attribute:: body

            If the event has a message, reason or a similar thing,
            you will find it in body.

        .. attibute:: target

            The target of the action, a channel if it is a channel
            message, the bot's nick if it is a private one or anything
            else.
    """

    def __init__(self, name=None, user=None, target=None, body=None):
        self.name = name
        self.user = user
        self.body = body
        self.target = target
        self._nick = False
        self._ident = False
        self._host = False

    def _splitnickidenthost(self):
        split = self.user.split('!')
        if len(split) == 1:
            return (None, None, None)
        nick = split[0]
        split = split[1].split('@')
        return (nick, split[0], split[1])

    @property
    def nick(self):
        if self._nick == False:
            self._nick = self._splitnickidenthost()[0]
        return self._nick

    @property
    def ident(self):
        if self._ident == False:
            self._ident = self._splitnickidenthost()[1]
        return self._ident

    @property
    def host(self):
        if self._host == False:
            self._host = self._splitnickidenthost[2]
        return self._host


class Hook(object):

    """
        This is just a possible implementation for a hook. Every hook
        that registers itself with the bot has to implement two
        functions:


            :func:`__init__`
            :func:`match`
            :func:`call`

        Read these functions documentation to see what they should do.

        Every hook that actually is supposed to be used, has to be
        prefixed by the @Bot.hook decorator. Doing so automatically
        adds the hook to the bot. The hook will be instantiated **once**
        on startup and then kept in memory until the bot dies.

        This means you can do some magic processing like reading config
        files and stuff in the beginning. As soon as your bot will be
        initialized there will be a bot instance present although
        you won't be able to send data in the beginning.

        You can check out the default alebot plugins for examples on
        how to write plugins.
    """

    def __init__(self, bot):
        """
            The :func:`__init__` function does not have to be overriden.
            It is expected to accept one parameter:

                :param bot: the bot instance

            It should save the bot instance to itself (as this
            implementation does). The bot instance can be used to
            easily send data, change the nick or similar stuff.
        """
        self.bot = bot

    def send_raw(self, data):
        """
            This function is just a shortcut to func:`Bot.send_raw`.
        """
        self.bot.send_raw(data)

    def match(self, event):
        """
            This function is used to evaluate whether the hook wants
            to react to the event that is passed on. It has to accept
            one parameter:

                :param event: an instance of the :class:`Event` class

            Although theoretically possible I recommend to separate
            the evaluation of a match and the actual reaction for the
            code's clearnesses sake.

            This way it is very easy to determine what triggers this
            hook.

                :returns: Either `True` or `False`, depending on
                whether a match is given or not.

            As this is a callback you have very high flexibility
            regarding your matching. You can match combinations of
            nick, ident, host, events, target and body.

            Check out the :class:`Event` class to see what event data
            is available.

            You can also use a regex or vary matches based on the time
            or the weather. Whatever you want.
        """
        raise NotImplementedError()

    def call(self, event):
        """
            In case that your :func:`match` function returned `True`
            this function will be called. It will again receive:

                :param event: an instance of the :class:`Event` class

            Now you are free to send data or do whatever you have to
            do.
        """
        raise NotImplementedError()
