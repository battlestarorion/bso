"""
Comsystem command module.

Comm commands are OOC commands and intended to be made available to
the Account at all times (they go into the AccountCmdSet). So we
make sure to homogenize self.caller to always be the account object
for easy handling.

"""
from evennia.commands.default.comms import CmdPage
from evennia.comms.models import Msg
from evennia.utils import create, utils


def parse_inline_pose(raw_pose=None):
    """
    Helper function to process inline supported pose syntax (', :, ;, ,, \\) such as 'page :my emote'
    Can be used to process straight up pose command syntax by passing the cmdstring
    Returns a dictionary: {"cmd": "<pose_cmd>", "body": "<parsed_message_body>"}
    """
    # To reduce str.startswith() calls
    cmd = raw_pose[:1]
    msg_body = raw_pose

    # Handle command that is > one character
    if raw_pose.startswith('\\\\'):
        cmd = '\\\\'
        msg_body = raw_pose[2:]
    elif cmd == ';':
        msg_body = raw_pose[1:]
    elif cmd == ':':
        msg_body = " %s" % raw_pose[1:].strip()
    # raw_pose does not have inline pose
    elif cmd not in [",", "'"]:
        cmd = None
    return {"cmd": cmd, "body": msg_body}


class CmdPage(CmdPage):
    """
    send a private message to another account

    Usage:
      page[/switches] [[<account>,<account>,... = ]<message>]
      pages [<number>]

    Aliases:
      p (page alias)
      tell (page alias)

    Switches:
      last - shows who you last messaged (page default)
      list - show last <number> of pages sent/received (pages default)

    Send a message to target user (if online). If no
    account(s) are given, but a message is provided, the message
    is sent to the last account(s) paged.

    The following pose commands are supported as message prefixes:
       ', ;, :, \\, and ,
    """
    aliases = CmdPage.aliases + ['p', 'pages']
    arg_regex = r"\s.+|/.+|$"

    def func(self):
        """Implement function using the Msg methods"""

        # Since account_caller is set above, this will be an Account.
        caller = self.caller

        # get the messages we've sent (not to channels)
        pages_we_sent = Msg.objects.get_messages_by_sender(caller, exclude_channel_messages=True)
        # get last messages we've got
        pages_we_got = Msg.objects.get_messages_by_receiver(caller)

        if 'last' in self.switches or ('pages' != self.cmdstring and not self.args and not self.switches):
            if pages_we_sent:
                recv = ",".join(obj.key for obj in pages_we_sent[-1].receivers)
                self.msg("You last paged |c%s|n: %s" % (recv, pages_we_sent[-1].message))
                return
            else:
                self.msg("You haven't paged anyone yet.")
                return

        if 'list' in self.switches or ('pages' == self.cmdstring and not self.rhs):
            pages = pages_we_sent + pages_we_got
            pages.sort(lambda x, y: cmp(x.date_created, y.date_created))

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: pages [number]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "|w%s|n |c%s|n to |c%s|n: %s"
            lastpages = "\n ".join(template %
                                   (utils.datetime_format(page.date_created),
                                    ",".join(obj.key for obj in page.senders),
                                    "|n,|c ".join([obj.name for obj in page.receivers]),
                                    page.message) for page in lastpages)

            if lastpages:
                string = "Your latest pages:\n %s" % lastpages
            else:
                string = "You haven't paged anyone yet."
            self.msg(string)
            return

        # We are sending. Build a list of targets

        if (not self.lhs and self.rhs) or (self.lhs and not self.rhs):
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to page?")
                return
        else:
            receivers = self.lhslist

        recobjs = []
        for receiver in set(receivers):
            if isinstance(receiver, basestring):
                pobj = caller.search(receiver)
            elif hasattr(receiver, 'character'):
                pobj = receiver
            else:
                self.msg("Who do you want to page?")
                return
            if pobj:
                recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to page.")
            return

        header = "|wAccount|n |c%s|n |wpages:|n" % caller.key
        # Handle non-mux page-last recipients style of 'page <msg>'
        if self.lhs and not self.rhs:
            message = self.lhs
        else:
            message = self.rhs

        # Parse any inline supported posing into parts
        message_parts = parse_inline_pose(message)

        if not message_parts["cmd"] or message_parts["cmd"] == '\\\\':
            message = message_parts["body"]
        # Add an actor
        else:
            message = "%s%s" % (caller.key, message_parts["body"])

        # create the persistent message object
        create.create_message(caller, message,
                              receivers=recobjs)

        # Add wrapping punctuation
        if not message_parts["cmd"]:
            message = "'%s'" % message

        # tell the accounts they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            if not pobj.access(caller, 'msg'):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            pobj.msg("%s %s" % (header, message))
            if hasattr(pobj, 'sessions') and not pobj.sessions.count():
                received.append("|C%s|n" % pobj.name)
                rstrings.append("%s is offline. They will see your message if they list their pages later."
                                % received[-1])
            else:
                received.append("|c%s|n" % pobj.name)
        if rstrings:
            self.msg("\n".join(rstrings))
        self.msg("You paged %s with: %s" % (", ".join(received), message))
