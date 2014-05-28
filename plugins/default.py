from alebot import Alebot, Hook


class ConnectionReadyHook(Hook):

    """
        This is a hook that can be subclassed in case you want to react
        on a irc connection that is ready for commands. It waits for
        the end of the motd, or the message that there is no motd.

        The :func:`match` function was implemented to listen to the
        correct events. You will just have to overwrite the :func`call`
        to actually do something.
    """

    def match(self, event):
        return (event.name == '376' or event.name == '422')


class CommandHook(Hook):
    """
        This is a hook that can be subclassed in case you want to react
        to a message on a channel or in private. It will react to the
        bot's current nickname followed by a colon and the command
        specified in the command attribute.
    """

    command = None

    def match(self, event):
        return (event.name == 'PRIVMSG' and event.body == '%s: %s' % (
            self.bot.config.get('nick'), self.command))


class CommandParamHook(Hook):

    """
        In case you want your command to take parameters, too.
    """

    def match(self, event):
        return (event.name == 'PRIVMSG' and event.body.startswith('%s: %s ' %
                (self.bot.config.get('nick'), self.command)))


@Alebot.hook
class SocketConnectedHook(Hook):

    """
        As the bot does nothing itself, this plugin takes care of
        identifying the bot with the server. Yeah, seriously.

        It uses the made up `SOCK_CONNECTED` event that is not even
        an actual IRC event..
    """

    def match(self, event):
        return (event.name == 'SOCK_CONNECTED')

    def call(self, event):
        self.bot.logger.info("Socket is ready, logging in.")
        self.send_raw("NICK %s" % self.bot.config['nick'])
        self.send_raw("USER %s * %s :%s" % (
            self.bot.config['ident'],
            self.bot.config['ident'],
            self.bot.config['realname']
        ))


@Alebot.hook
class PingPong(Hook):

    """
        As the bot does nothing by itself, this plugin takes care of
        sending PONGs as answer to pings, as the bot won't even do that.

        It matches the `PING` event to do that.
    """

    def match(self, event):
        return (event.name == 'PING')

    def call(self, event):
        self.bot.logger.info('Received ping, sending pong.')
        self.send_raw('PONG %s' % event.body)
