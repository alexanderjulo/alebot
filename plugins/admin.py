from alebot import Alebot, Hook, Event
auth = Alebot.get_plugin('auth')


@Alebot.hook
class SaveHook(auth.AdminCommandHook):

    """
        Save current config state to disk.
    """

    command = 'save'

    def call(self, event):
        print("Saving")
        self.bot.save_config()
        self.msg(event.target, "saved.")
        event = Event('SAVE')
        self.bot.call_hooks(event)


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
