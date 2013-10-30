from alebot import Alebot, Hook
from functools import wraps

default = Alebot.get_plugin('default')

def admin_required(f):
    @wraps(f)
    def auth_and_match(self, event):
        config = self.bot.config.get('auth', {})
        if not event.nick or not event.nick in config.get('admins', []):
            return False
        return f(self, event)
    return auth_and_match


class AdminCommandHook(default.CommandHook):

    """
        Just a shortcut for simple commands that require admin
        permissions.
    """

    @admin_required
    def match(self, event):
        print(self)
        return default.CommandHook.match(self, event)
