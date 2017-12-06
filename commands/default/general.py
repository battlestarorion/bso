"""
General Character commands usually available to all characters.
"""
from evennia.utils import utils, evtable
from evennia.typeclasses.attributes import NickTemplateInvalid
from evennia.commands.default.general import CmdNick


class AccountAwareCmdNick(CmdNick):
    """
    Character nicks that are able to list their global nicks from Account
    """

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
