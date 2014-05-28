import os
import asyncore
import socket
from asynchat import async_chat
import pkgutil
import imp
import json
import threading
import logging


class IRCCommandsMixin(object):

    """
        This is just a helpful mixin to provide a few basic irc
        command wrappers to different classes.
    """

    def msg(self, target, text):
        """
            Send a message to a target.

                :param target: either a channel (with prefix) or a nick
                :param text: the contents of the message
        """
        self.send_raw("PRIVMSG %s :%s" % (target, text))

    def join(self, channel):
        """
            Join a channel.

                :param channel: the channel to join (with prefix)
        """
        self.send_raw("JOIN %s" % (channel))

    def part(self, channel, reason='Part.'):
        """
            Part a channel.

                :param channel: the channel to part (with prefix)
        """
        self.send_raw("PART %s :%s" % (channel, reason))

    def quit(self, reason='Quit.'):
        """
            Quit the server.

                :param reason: the reason for the quit (will be shown
                    to other users in common channels)
        """
        self.send_raw("QUIT :%s" % reason)


class Event(object):

    """
        The :class:`.Event` class is used to store data about the
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

        .. attribute:: target

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

    def __repr__(self):
        return '<alebot.Event %s>' % (self.name)

    def _splitnickidenthost(self):
        if not self.user:
            return (None, None, None)
        split = self.user.split('!')
        if len(split) == 1:
            return (None, None, None)
        nick = split[0]
        split = split[1].split('@')
        return (nick, split[0], split[1])

    @property
    def nick(self):
        if self._nick is False:
            self._nick = self._splitnickidenthost()[0]
        return self._nick

    @property
    def ident(self):
        if self._ident is False:
            self._ident = self._splitnickidenthost()[1]
        return self._ident

    @property
    def host(self):
        if self._host is False:
            self._host = self._splitnickidenthost[2]
        return self._host


class Hook(IRCCommandsMixin, object):

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

        If you want to log data, it is recommended to access the bot's
        logger using `self.bot.logger`. It supports python's usual
        logging infrastructure and thus functions like `debug`, `info`,
        `warn` and `error`.
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

                :param event: an instance of the :class:`.Event` class

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

            Check out the :class:`.Event` class to see what event data
            is available.

            You can also use a regex or vary matches based on the time
            or the weather. Whatever you want.
        """
        raise NotImplementedError()

    def call(self, event):
        """
            In case that your :func:`match` function returned `True`
            this function will be called. It will again receive:

                :param event: an instance of the :class:`.Event` class

            Now you are free to send data or do whatever you have to
            do.
        """
        raise NotImplementedError()


class Task(threading.Thread):

    """
        This class can be used to do stuff in the background. It can be
        used for everything that might take some time and should not
        block the bot in the meantime.

        It expects the following parameters:

            :param hook: the current hook instance (the active plugin)
            :param event: the current event

        You can basically overwrite the init event any pass less data,
        the example data her is just for convenience.

        You will have to overwrite :func:`do` though. See the
        functions documentation for more information.

        The task can be started using the :func:`start` function.
    """

    def __init__(self, hook, event):
        threading.Thread.__init__(self)
        self.bot = hook.bot
        self.hook = hook
        self.event = event

    def do(self):
        """
            Override this with whatever your backgroundtask is
            supposed to do. Your function should take the :class:`.Task`
            instance as a parameter.
        """
        raise NotImplementedError()

    def run(self):
        """
            The run function is overwritten to call the do function
            and catch any exceptions. This way bot crashes should be
            avoided. So if you would like your bot to be stable, please
            do not overwrite this, but the :func:`do` function.
        """
        try:
            self.do()
        except Exception as e:
            self.logger.error("Task %s failed: %s" % (self, e))


class Alebot(async_chat, IRCCommandsMixin):

    """
        The main bot class, where all the magic happens.

        This class handles the socket and all incoming and outgoing
        data. This classes methods should be used for sending data.

        It keeps an index of loaded plugins and helps with the
        management of requirements.

        To interact witht he bot it supplies a hook function that can
        be used to register callbacks with the bot.

        Please check out :class:`.Hook` and :func:`hook` to find
        out how hooking your plugins in works.

        Please note that this bot does absolutely nothing by itself.

        It won't even answer pings or identify. But there are some
        system plugins to do that. Check the plugins folder.

        .. attribute:: config

            Holds the bot configuration.

        .. attribute:: Hooks

            Registered hooks

        .. attribute:: Plugins

            Registered modules
    """

    Hooks = []
    Plugins = {}
    _Paths = None
    path = None
    Logger = logging.getLogger('alebot')

    def __init__(self, path=None, disableLog=False):
        """
            Initiates the parent and some necessary variables.

            Then reads the configuration, finds all the plugins and their
            hooks and instantiates them.

                :param path: path to the `config.json` and plugins folder.
        """
        # unless we get disableLog we log level info to stdout until reading
        # the config file
        if not disableLog:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel("INFO")
        self.logger.info("Initiation the bot..")

        # saving the path
        if path:
            self.path = path
        else:
            self.path = os.getcwd()
        self.logger.info("Using '%s' as bot path." % self.path)

        # system crap
        async_chat.__init__(self)
        self.set_terminator('\r\n')
        self.buffer = ''

        # access self.paths to init Alebot.Paths
        self.paths

        # load the default config
        self.config = {
            'nick': 'alebot',
            'ident': 'alebot',
            'realname':
            'alebot python irc bot. https://github.com/alexex/alebot',
            'server': 'irc.freenode.net',
            'port': 6667,
            'logToStdout': True,
            'logLevel': 'INFO',
            'logFormatter': '%(asctime)s - %(levelname)s - %(message)s',
            'logFile': False
        }

        # load an eventual configuration
        self.load_config()

        # load plugins
        self.load_plugins()

        # activate plugin hooks
        self.activate_hooks()

    @property
    def logger(self):
        """
            To enable access to the logger from both class- and object
            methods, this property is available.
        """
        return self.__class__.Logger

    @classmethod
    def Paths(cls, path=None):
        """
            The path storage. Use this to get the user & the systempath!
        """
        if not cls._Paths:
            paths = []

            # add system plugin path
            if __file__:
                paths.append(os.path.join(os.path.dirname(__file__),
                             'plugins'))

            # if an additional path was given, check for user plugins
            if path:
                userpath = os.path.join(path, 'plugins')
                if not os.path.exists(path):
                    cls.Logger.warn("User plugin path '%s' does not exist!" %
                                    userpath)
                elif not os.path.isdir(path):
                    cls.Logger.warn("User plugin path '%s' is not a dir." %
                                    userpath)
                else:
                    cls.Logger.info("User plugin path '%s' added.", userpath)
                    paths.append(userpath)
            else:
                cls.Logger.warn("No user plugin path given!")
            cls._Paths = paths
        return cls._Paths

    @property
    def paths(self):
        """
            Shortcut to class-level Paths storage.
        """
        return self.__class__.Paths(self.path)

    def configure_logging(self):
        """
            Depending on the configuration the log level and eventual
            handlers for the logging have to be configured, which is
            what this function does.
        """
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.setLevel(self.config.get('logLevel'))
        formatter = logging.Formatter(self.config.get('logFormatter'))
        if self.config.get('logToStdout'):
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        if self.config.get('logFile'):
            handler = logging.FileHandler(self.config.get('logFile'))
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @classmethod
    def load_plugins(cls, path=None):
        """
            Will load all the plugins from the plugin folder. It will
            only load them though! The plugins still have to register
            themselves with the :func:`hook` function, if they want to
            interact with the bot.

            This function does not do anything yet. Plugins have to be
            in the the same file as the bot itself.
        """
        cls.Hooks = []
        cls.Plugins = {}

        for _, name, _ in pkgutil.iter_modules(cls.Paths()):
            cls.load_plugin(name)

    @classmethod
    def load_plugin(cls, name, path=[]):
        """
            Load a specific plugin. This will try to find a specific
            plugin, load it and save it to the :class:`.Alebot` class,
            so that it can be retrieved later on.

            It will also make sure, that plugins are only loaded once.
        """
        if not path:
            path = cls.Paths()
        fid, pathname, desc = imp.find_module(name, path)
        if cls.Plugins.get(name):
            return
        try:
            plugin = imp.load_module(name, fid, pathname, desc)
            cls.Plugins[name] = plugin
            cls.Logger.info("Loaded plugin '%s' from '%s'" % (name, pathname))
        except Exception as e:
            cls.Logger.warning("Could not load plugin '%s': %s" %
                               (pathname, e))
        if fid:
            fid.close()

    @classmethod
    def get_plugin(cls, name):
        """
            This is mainly a helper for inter dependency between
            plugins. If one plugin requires another one, it can get
            to it with this function. If the plugin has not been
            loaded yet, it will try to load it. If it fails or does
            not exist, the requiring plugin will also fail to load.
        """
        if not cls.Plugins.get(name):
            cls.load_plugin(name)
        return cls.Plugins[name]

    def load_config(self):
        """
            Will open the local config file `config.json` and load
            it as json. Will only accept a json object.

            There are no required values. The file itself it optional.
            The bot will supply default values, if there are none
            specified.

            Alebot itself makes use of the following options:

            - ``nick``
            - ``ident``
            - ``realname``
            - ``server``
            - ``port``

            Any additional option can be configured. Plugin developers
            are encouraged to specifiy plugin objects with own
            configuration, as long as they make sure to use a specific
            name to avoid conflicts.
        """
        error = False
        path = os.path.join(self.path, 'config.json')
        try:
            f = open(path, 'r')
            config = json.load(f)
            f.close()
            self.config = dict(self.config.items() + config.items())
        except Exception as e:
            error = e
            config = False

        # we need this little workaround to make sure that the config loading
        # is logged according to the given settings.
        self.configure_logging()
        if config:
            self.logger.info("Configuration loaded.")
        else:
            self.logger.info("No configuration loaded: %s" % error)

    def save_config(self):
        """
            Save the current configuration to file.
        """

        try:
            f = open('config.json', 'w')
            json.dump(self.config, f, indent=4)
            f.close()
            self.logger.info("Configuration saved.")
        except Exception as e:
            self.logger.info("Configuration could not be saved: %s" % e)

    @classmethod
    def hook(cls, Hook):
        """
            This method will register a hook with the bot. It is
            supposed to be used as a decorator, but can also be used
            as a normal function. Please see the :class:`.Hook` class
            documentation for an overview what a hook should look like.

            This method will save the :class:`.Hook` class with the
            :class:`.Alebot` class until the :func:`__init__` function
            instantiates the hooks.
        """
        cls.Hooks.append(Hook)
        return Hook

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
            try:
                if (hook.match(event)):
                    hook.call(event)
            except Exception as e:
                self.logger.error("Hook %s failed: %s" % (hook, e))

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

            if(len(line) >= 4):
                event.body = line[3][1:]

        elif (line[0] == 'PING'):
            event.name = line[0]
            event.body = line[1][1:]
        elif (line[0] == 'ERROR'):
            event.name = 'ERROR'
            event.body = ' '.join(line[1:])[1:]
        else:
            event.name = 'UNKNOWN'
            event.body = ' '.join(line)

        self.call_hooks(event)

    def send_raw(self, data):
        """
            Sends raw commands to the server. Only adds CLRF as a suffix.

            :param data: the IRC command and body to send, fully
                formatted as such.
        """
        crlfed = '%s\r\n' % data
        self.push(crlfed.encode('utf-8', 'ignore'))
