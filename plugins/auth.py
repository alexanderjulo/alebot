from alebot import Alebot, Hook
from functools import wraps

def admin_required(f):
    @wraps(f)
    def auth_and_match(self, event):
        config = self.bot.config.get('auth', {})
        if not event.nick or not event.nick in config.get('admins', []):
            return False
        return f(self, event)
    return auth_and_match
