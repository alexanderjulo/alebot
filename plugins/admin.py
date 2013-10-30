from alebot import Alebot, Hook, Event
auth = Alebot.get_plugin('auth')

@Alebot.hook
class ReloadHook(auth.AdminCommandHook):

    """
        Reloads config and plugins on request.
    """

    command = 'reload'

    def call(self, event):
        print("Reloading")
        self.bot.load_config()
        self.bot.load_plugins()
        self.bot.activate_hooks()
        self.msg(event.target, "reloaded.")
        event = Event('RELOAD')
        self.bot.call_hooks(event)
