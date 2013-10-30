from alebot import Alebot, Hook, Event
from plugins.auth import admin_required

@Alebot.hook
class ReloadHook(Hook):

    """
        Reloads config and plugins on request.
    """

    @admin_required
    def match(self, event):
        return (event.name == 'PRIVMSG' and event.body == '%s: %s' % (
                    self.bot.config.get('nick'), 'reload'))

    def call(self, event):
        print("Reloading")
        self.bot.load_config()
        self.bot.load_hooks()
        self.bot.activate_hooks()
        self.msg(event.target, "reloaded.")
        event = Event('RELOAD')
        self.bot.call_hooks(event)
