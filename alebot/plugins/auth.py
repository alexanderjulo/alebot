from alebot import Alebot
from functools import wraps

default = Alebot.get_plugin('default')


def admin_required(f):
    """
        You can decorate the `match` functions of your :class:`Hook` classes
        with this function. It will assure, that only auth admins can use
        the command.

        After verifying this, your normal match will be excuted.
    """
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
        return super(AdminCommandHook, self).match(event)


class AdminCommandParamHook(default.CommandParamHook):

    """
        Just a shortcut for simple commands that require admin
        permissions.
    """

    @admin_required
    def match(self, event):
        return super(AdminCommandParamHook, self).match(event)


class AdminManager(object):

    """
        A wrapper around the config file to improve the auth config
        handling.
    """

    def check_config(self):
        """
            Make sure that the config section exists.
        """
        if not self.bot.config.get('auth'):
            self.bot.config['auth'] = {}

    def add_admin(self, nick):
        """
            Add an admin to the list of admins.
        """
        if not self.bot.config['auth'].get('admins'):
            self.bot.config['auth']['admins'] = [nick]
        elif not nick in self.bot.config['auth']['admins']:
            self.bot.config['auth']['admins'].append(nick)
        return True

    def delete_admin(self, nick):
        """
            Remove an admin from the list of admins.
        """
        if nick in self.bot.config['auth'].get('admins', []):
            self.bot.config['auth']['admins'].remove(nick)
        return True


@Alebot.hook
class AdminManagementHook(AdminManager, AdminCommandParamHook):

    """
        Add and remove admins via irc commands.
    """

    command = 'admin'

    def msg_syntax_error(self, event):
        self.msg(event.target, "The required syntax is: <action> [<nick>]")

    def call(self, event):
        print "called."

        args = event.body.split(' ')
        if (len(args) < 3):
            self.msg_syntax_error(event)
            return
        action = args[2]

        self.check_config()

        if action == 'list':
            admins = ''
            for admin in self.bot.config['auth'].get('admins', []):
                admins += "%s, " % admin
            admins = admins[:-2]
            self.msg(event.target, "Admins are: %s" % admins)
            return

        if(len(args) < 4):
            self.msg_syntax_error(event)

        nick = args[3]

        if action == 'add':
            self.add_admin(nick)
            self.msg(event.target, "%s is now admin." % nick)
        elif action == 'remove' or action == 'delete':
            self.delete_admin(nick)
            self.msg(event.target, "%s is now no admin nomore." % nick)
        else:
            self.msg(event.target, "Unknown action: %s" % action)
