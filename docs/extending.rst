Extending the bot
=================

If you came to use alebot, you probably want to do one thing: extend and
customize it. Customizing is really easy! All the customization is done using hooks.

To write your own extension/plugin just create a new python script
within the ``plugins/`` directory, upon the next reload/start it will
automatically be loaded.

Now you have your first plugin but unfortunately it does not do anything
yet. We will change that now::

    # first we import the alebot and the hook class
    from alebot import Alebot, Hook

    # now we write our first hook that will just echo whatever someone
    # writes.
    # to do so we just subclass Hook (this is not required, but it provides
    # us with helpful infrastructure we don't have to take care of ourselves)
    class EchoHook(Hook):

        # every hook has to specify a match function that will check
        # whether this hook should do something now
        def match(self, event):
            # every hook gets a event object passed (check the Event class
            # for more info) that contains information on the event that is
            # occuring right now.
            # we just check whether the event is a message or not and return
            # the result of that check
            return (event.name == "PRIVMSG") 

        # the second requirement for every hook is a call function, that
        # will be executed if the match function returned True.
        def call(self, event):
            # it will be again passed the event object so you can use that
            # data
            # we just check whether the target of the message was the bot
            # in which case it would have been a private message or a
            # channel. to do so we access the bot's config!
            if (event.target == self.bot.config.get('nick')):
                target = event.nick
            else:
                target = event.target

            # now that we know where to echo to, we use the message's
            # body and send it to the server:
            self.msg(target, event.body)

            # aaaand we're done!

That was easy, right? The only problem is, that this hook will never be
called as it is right now. You will have to let your bot know, that you
want it to be executed. This is necessary, as you could not build
helper classes that are not supposed to be executed themselves.
Fortunately it is very easy to let your bot know that you want the hook
to be executed. You can just add a decorator to your class as follows::

    from alebot import Alebot, Hook

    @Alebot.hook
    class EchoHook(Hook):
        ....



Now that was a very simple plugin. Now we will use a `Task` object to
get a delay (or do something possibly time intensive) without blocking
the execution of other hooks::

    from alebot import Alebot, Hook, Task
    # we import sleep to delay this stuff
    from time import sleep

    # we subclass Task to get all the necessary infrastructure!
    class DelayedEchoTask(Task):

        # now we only need to overwrite the do function to tell the
        # background task what it should do
        def do(self):
            # to make the echo more annoying we will just wait a few
            # seconds before echoing. Using a task to do this we don't
            # block it from doing more important stuff
            sleep(5)
            # thanks to subclassing Task all this infrastructure is
            # already available: we have access to the event and the
            # bot. The logic is the same as in the non delayed echo
            # version.
            if (self.event.target == self.bot.config.get('nick')):
                target = self.event.nick
            else:
                target = self.event.target
            self.bot.msg(tartget, self.event.body)


    # we again use the decorator to activate the hook.
    @Alebot.hook
    class DelayedEchoHook(Hook):
        
        # same logic as above applies for matching
        def match(self, event):
            return (event.name == "PRIVMSG")

        # the calling is a little different
        def call(self, event):
            # instead of delaying and blocking here, we initiate a task
            # object of our custom task class (and pass on hook & event):
            task = DelayedEchoTask(self, event)

            # and then we run it using the run method. This is important
            # as it will automatically catch possible errors and actually
            # run the task in the background. If you just call do, you
            # will still block execution!
            task.run()

            # the task is threaded away and this line will be executed
            # immediately
            self.bot.logger.debug("delaying echo in the background!")

There are some additional helper classes, especially regarding matching
in Hooks in the ``default`` module that you might want to take a look at.

Besides that you can always look at the system plugins documentation and
source for some inspiration of how extending alebot works.
