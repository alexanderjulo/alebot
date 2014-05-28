System Plugins
==============

Alebot per se provides near to no functionality. It will merely connect
to the server, but won't even initiate the irc auth according to IRC. It
also will not send ping/pongs or anything else.

As the bot is pretty useless without this functionality though, there
are some default plugins provided that will do all this quite necessary
stuff for you and provide additional functionality that might be
expected of an irc bot.

Default
-------

This is the plugin that supplies absolute minimum functionality. In it 
are both the hook for ping/pong events and it initiate the irc auth.

Do not disable it or your bot won't do anything at all.

Additionally this module supplies some helper hooks that don't do
anything but can be subclassed to use to write plugins easier. Check the
api documentation for more details.


Auth
----

The auth module provides capabilites for basic administrator management
and authentication. It exposes a few commands to channels and privates.

You can use commands in the following format in IRC to acces the functionality::

    <nick of the bot>: admin <list>
    <nick of the bot>: admin <add> <nick>
    <nick of the bot>: admin <remove/delete> <nick>

To list currently configured admins, add a new admin or remove an admin.


Admin
-----

This plugin provides some bot wide functionality to administrators. It
thus requires the auth plugin. If you are configured as an administrator you can
use one of the following commands::

    <nick of the bot>: reload
    <nick of the bot>: save

If you reload all plugins will be reloaded and eventual changes in source
code and config will be accounted for. If you save the current in bot state
of the config file will be written to disk.


Channels
--------

The channels module will make the bot join the channels specified in the
config upon successful irc auth.

The channels should be configured as a list of strings in the ``channels``
setting in the config file, i.e.::

    {"channels": ["#channel1", "#channel2"]}

Shortlink
---------

Shortlink is the only plugin that will not be loaded by default. This is
due to the fact that it requires the ``requests`` module which I refuse
to make a hard dependency just for this. You can enable it by installing
the module. It will automatically shorten all urls longer than 50 chars
using the google shortener. This will be done in the background so that
the shortening does not block the bot itself.

You can configure the minimum required length of a link to shorten in
the config file using the ``shortlink`` key::

    {"shortlink": {"length": 30}}
