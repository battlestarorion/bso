"""
Commands that are available from the connect screen.
"""
from evennia.commands.default.unloggedin import CmdUnconnectedHelp
import types
from evennia.commands.default.account import CmdWho


class CmdUnconnectedHelp(CmdUnconnectedHelp):
    def func(self):
        """Shows help"""

        string = \
            """
You are not yet logged into the game. Commands available at this point:

  |wcreate|n - create a new |wOOC|n account
  |wconnect|n - connect with an existing account
  |wlook|n - re-show the connection screen
  |wwho|n - show which players are connected
  |whelp|n - show this help
  |wencoding|n - change the text encoding to match your client
  |wscreenreader|n - make the server more suitable for use with screen readers
  |wquit|n - abort the connection

First create an |wOOC|n account e.g. with |wcreate Anna c67jHL8p|n
(If you have spaces in your name, use double quotes: |wcreate "Anna the Barbarian" c67jHL8p|n
Next you can connect to the game: |wconnect Anna c67jHL8p|n

You can use the |wlook|n command if you want to see the connect screen again.

"""
        self.caller.msg(string)


class CmdSessionWho(CmdWho):
    __doc__ = CmdWho.__doc__

    class PartialMockAccount(object):
        """
        Partially mocked singleton, so it is kept here.
        """
        def __new__(cls):
            if not hasattr(cls, 'instance'):
                cls.instance = super(CmdSessionWho.PartialMockAccount, cls).__new__(cls)

            return cls.instance

        def check_permstring(self, permission=None):
            return False

    @staticmethod
    def _session_msg_wrapper(target, msg=None):
        if msg:
            target.caller.msg(msg)

    def func(self):
        """
        Get all connected accounts by polling session.
        """

        if not self.account:
            # This is a session.
            self.msg = types.MethodType(CmdSessionWho._session_msg_wrapper, self)
            self.account = self.PartialMockAccount()

        super(CmdSessionWho, self).func()
