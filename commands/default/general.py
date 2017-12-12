"""
General Character commands usually available to all characters.
"""
from evennia.utils import utils, evtable
from evennia.typeclasses.attributes import NickTemplateInvalid
from evennia.commands.default.general import CmdNick, CmdPose, CmdWhisper
from comms import InlinePoseHelper


class AccountAwareCmdNick(CmdNick):
    __doc__ = CmdNick.__doc__

    # Copy/pasted/modified from upstream.
    # This is done so we have complete control over the display and avoid situations where the account nicks display but
    # the character ones return 'No nicks defined.' which looks like an error.
    def func(self):
        """Create the nickname"""
        caller = self.caller
        switches = self.switches
        nicktypes = [switch for switch in switches if switch in ("object", "account", "inputline")] or ["inputline"]

        nicklist = utils.make_iter(caller.nicks.get(return_obj=True) or [])
        acct_nicklist = utils.make_iter(caller.account.nicks.get(return_obj=True) or [])

        if 'list' in switches or self.cmdstring in ("nicks", "@nicks"):

            if not nicklist and not acct_nicklist:
                string = "|wNo nicks defined.|n"
            else:
                acct_table = ''
                table = ''
                if acct_nicklist:
                    acct_table = "|wDefined Global Nicks:|n\n%s" % self.build_nick_table(nicklist=acct_nicklist)
                if nicklist:
                    table = "|wDefined Character Nicks:|n\n%s" % self.build_nick_table(nicklist=nicklist)
                string = "{}{}{}".format(acct_table, "\n" if acct_table and table else '', table)
            caller.msg(string)
            return

        if 'clearall' in switches:
            caller.nicks.clear()
            caller.msg("Cleared all nicks.")
            return

        if not self.args or not self.lhs:
            caller.msg("Usage: nick[/switches] nickname = [realname]")
            return

        nickstring = self.lhs
        replstring = self.rhs
        old_nickstring = None
        old_replstring = None

        if replstring == nickstring:
            caller.msg("No point in setting nick same as the string to replace...")
            return

        # check so we have a suitable nick type
        errstring = ""
        string = ""
        for nicktype in nicktypes:
            oldnick = caller.nicks.get(key=nickstring, category=nicktype, return_obj=True)
            if oldnick:
                _, _, old_nickstring, old_replstring = oldnick.value
            else:
                # no old nick, see if a number was given
                arg = self.args.lstrip("#")
                if arg.isdigit():
                    # we are given a index in nicklist
                    delindex = int(arg)
                    if 0 < delindex <= len(nicklist):
                        oldnick = nicklist[delindex - 1]
                        _, _, old_nickstring, old_replstring = oldnick.value
                    else:
                        errstring += "Not a valid nick index."
                else:
                    errstring += "Nick not found."
            if "delete" in switches or "del" in switches:
                # clear the nick
                if old_nickstring and caller.nicks.has(old_nickstring, category=nicktype):
                    caller.nicks.remove(old_nickstring, category=nicktype)
                    string += "\nNick removed: '|w%s|n' -> |w%s|n." % (old_nickstring, old_replstring)
                else:
                    errstring += "\nNick '|w%s|n' was not deleted." % old_nickstring
            elif replstring:
                # creating new nick
                errstring = ""
                if oldnick:
                    string += "\nNick '|w%s|n' updated to map to '|w%s|n'." % (old_nickstring, replstring)
                else:
                    string += "\nNick '|w%s|n' mapped to '|w%s|n'." % (nickstring, replstring)
                try:
                    caller.nicks.add(nickstring, replstring, category=nicktype)
                except NickTemplateInvalid:
                    caller.msg("You must use the same $-markers both in the nick and in the replacement.")
                    return
            elif old_nickstring and old_replstring:
                # just looking at the nick
                string += "\nNick '|w%s|n' maps to '|w%s|n'." % (old_nickstring, old_replstring)
                errstring = ""
        string = errstring if errstring else string
        caller.msg(string)

    def build_nick_table(self, nicklist=None):
        if nicklist:
            table = evtable.EvTable("#", "Type", "Nick match", "Replacement")
            for inum, nickobj in enumerate(nicklist):
                _, _, nickvalue, replacement = nickobj.value
                table.add_row(str(inum + 1), nickobj.db_category, nickvalue, replacement)
            return table


class CmdPose(CmdPose):
    """
    strike a pose

    Usage:
      pose <pose text>
      pose's <pose text>

    Aliases:
      :<pose text> => Character <pose text>
      ;<pose text> => Character<pose text>
      \\<pose text> => <pose text>

    Example:
      pose is standing by the wall, smiling.
       -> others will see:
      Tom is standing by the wall, smiling.

    Describe an action being taken. The pose text will
    automatically begin with your name.
    """
    aliases = CmdPose.aliases + [';', '\\\\']

    def parse(self):
        """
        Custom parse the cases where the emote
        starts with some special letter, such
        as 's, at which we don't want to separate
        the caller's name and the emote with a
        space.
        """
        args = self.args
        if args and not args[0] in ["'", ":"] and self.cmdstring not in [';', '\\\\']:
            args = " %s" % args.strip()
        self.args = args

    def func(self):
        if not self.args:
            # Super func handles error message.
            pass
        elif self.cmdstring == "\\\\":
            msg = self.args
            self.caller.location.msg_contents(text=(msg, {"type": "pose"}),
                                              from_obj=self.caller)
            return
        super(CmdPose, self).func()


class CmdWhisper(CmdWhisper):
    __doc__ = """
    Speak privately as your character to another

    Usage:
      whisper <character> = <message>
      whisper <char1>, <char2> = <message>
      whisper <message>
      whisper

    Talk privately to one or more characters in your current location, without
    others in the room being informed.

    If characters are not given, the message is sent to the last character(s)
    whispered.

    If no arguments are given, then the command shows you which character(s) 
    where whispered to.
    """

    def parse(self):
        super(CmdWhisper, self).parse()
        caller = self.caller

        # If using the whisper to last whispered format
        if self.lhs and not self.rhs:
            last_recievers = caller.ndb.last_whisper_recievers
            if last_recievers:
                self.rhs = self.lhs
                self.lhs = last_recievers

    def func(self):
        """Run the whisper command"""

        caller = self.caller
        last_recievers = caller.ndb.last_whisper_recievers

        if not self.args:
            msg = "You last whispered to {recipients}.".format(recipients="|yno one|n" if not last_recievers else
            "|c%s|n" % last_recievers)
            self.msg(msg)
            return

        if not self.lhs or not self.rhs:
            caller.msg("Usage: whisper <character> = <message>")
            return

        receivers = [recv.strip() for recv in self.lhs.split(",")]

        receivers = [caller.search(receiver) for receiver in receivers]
        receivers = [recv for recv in receivers if recv]

        speech = self.rhs
        # If the speech is empty, abort the command
        if not speech or not receivers:
            return

        # Store non-persistent receivers for re-using
        caller.ndb.last_whisper_recievers = self.lhs

        parsed = InlinePoseHelper.parse(speech)
        parsed = InlinePoseHelper.prefix_actor_to_body(parsed, caller.key)

        # Call a hook to change the speech before whispering
        if InlinePoseHelper.is_speech(parsed):
            parsed['body'] = caller.at_before_say(parsed['body'], whisper=True, receivers=receivers)

        parsed = InlinePoseHelper.wrap_body(parsed, "'")
        speech = parsed['body']

        # no need for self-message if we are whispering to ourselves (for some reason)
        msg_self = None if caller in receivers else '{self} whisper to {all_receivers}: {speech}'
        msg_receivers = '{object} whispers: {speech}'
        say = caller.at_say(speech, msg_self=msg_self, receivers=receivers, msg_receivers=msg_receivers, whisper=True)
