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
        print("Socket is ready, logging in.")
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
        print('Received ping, sending pong.')
        self.send_raw('PONG %s' % event.body)


@Alebot.hook
class JoinOnConnect(ConnectionReadyHook):

    """
        Join channels defined in the config file options `channels` on
        connection. If there are any definied, if not, it does not
        join any channels.
    """

    def call(self, event):
        print("Joining channels..")
        channels = self.bot.config.get('channels', [])
        for channel in channels:
            self.send_raw('JOIN %s' % channel)


@Alebot.hook
class PrintAll(Hook):

    """
        Prints all server input to the terminal.
    """

    def match(self, event):
        return True

    def call(self, event):
        print(event.name, event.user, event.target, event.body)
