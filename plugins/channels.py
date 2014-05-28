from alebot import Alebot
default = Alebot.get_plugin('default')


@Alebot.hook
class JoinOnConnect(default.ConnectionReadyHook):

    """
        Join channels defined in the config file options `channels` on
        connection. If there are any definied, if not, it does not
        join any channels.
    """

    def call(self, event):
        self.bot.logger.info("Joining channels..")
        channels = self.bot.config.get('channels', [])
        for channel in channels:
            self.send_raw('JOIN %s' % channel)
