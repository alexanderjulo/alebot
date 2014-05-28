import re
import requests
import json
from alebot import Alebot, Hook, Task


@Alebot.hook
class ShortLink(Hook):

    """
        Shorten links that are too long.

        Tries to find all http links and spawns a background task
        that generates a goo.gl shortlink with the help of the google
        api.

        Use the config setting "shortlink": {"length": <int>}. If not
        specified links from 50 chars up will be converted, if
        specified from the given number of chars up.
    """

    url_regex = re.compile(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|"
        + "(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )

    def match(self, event):
        """
            Check whether the event is a message, whether an url is given
            and whether the url is long enough to match.
        """
        if (event.name != 'PRIVMSG'):
            return False
        length = self.bot.config.get('shortlink', {}).get('length', 50)
        match = self.url_regex.match(event.body)
        if (match and len(match.group(0)) >= length):
            return True
        return False

    def call(self, event):
        """
            Spawn background task with the url.
        """
        self.long_url = self.url_regex.match(event.body).group(0)
        task = RequestShortLink(self, event)
        task.start()


class RequestShortLink(Task):

    """
        Uses requests to rshorten the url with google.
        As soon as the answer is received, it sends the result to
        the channel.
    """

    def do(self):
        url = 'https://www.googleapis.com/urlshortener/v1/url'
        headers = {'content-type': 'application/json'}
        payload = {'longUrl': self.hook.long_url}
        r = requests.post(url, data=json.dumps(payload), headers=headers)

        self.bot.msg(self.event.target, r.json()['id'])
