# -*- coding: utf-8 -*-
"""
Connection screen

Texts in this module will be shown to the user at login-time.

Evennia will look at global string variables (variables defined
at the "outermost" scope of this module and use it as the
connection screen. If there are more than one, Evennia will
randomize which one it displays.

The commands available to the user when the connection screen is shown
are defined in commands.default_cmdsets. UnloggedinCmdSet and the
screen is read and displayed by the unlogged-in "look" command.

"""

from django.conf import settings
from evennia import utils

CONNECTION_PARTS = { 'default': """
|b==============================================================|n
 Welcome to |g{}|n, version {}!

 If you have an existing account, connect to it by typing:
      |wconnect <username> <password>|n
 If you need to create an account, type (without the <>'s):
      |wcreate <username> <password>|n

 If you have spaces in your username, enclose it in quotes.
 Enter |whelp|n for more info. |wlook|n will re-show this screen.
|b==============================================================|n""" \
    .format(settings.SERVERNAME, utils.get_evennia_version()),
    'custom_divider': """                       - .... .    ..-. --- -..- .... --- .-.. . """,
    'login_instructions_long': """ If you have an existing account, connect to it by typing:
      |wconnect <username> <password>|n
 If you need to create an account, type (without the <>'s):
      |wcreate <username> <password>|n""",
    'login_footer': """ Please do not include spaces in your username.
 Enter |whelp|n for login info or |wlook|n to show this again.""",
    'border_heavy': """|b==============================================================|n""",
    'border_light': """|b--------------------------------------------------------------|n""",
    'version_footer': """                       server {} - game {}|n""" \
	.format(utils.get_evennia_version(), 'tbd'),
    }

CONNECTION_SCREEN = """
{top_border}
 ___    __      
  ||he   ||-oxhole
   **    *  *  *
          *  ** 
  *        *    
                
                
  *           * 
                
    *          *
         **  *  
           *    
   *        *   
                
{divider}

{login_instructions}
{divider2}
{version}
{bottom_border}""" \
    .format(top_border=CONNECTION_PARTS['border_heavy'],
            divider=CONNECTION_PARTS['custom_divider'],
            login_instructions=CONNECTION_PARTS['login_footer'],
            divider2=CONNECTION_PARTS['border_light'],
            version=CONNECTION_PARTS['version_footer'],
            bottom_border=CONNECTION_PARTS['border_heavy'])

#CONNECTION_SCREEN = """
#|b==============================================================|n
# Welcome to |g{}|n, version {}!
#
# If you have an existing account, connect to it by typing:
#      |wconnect <username> <password>|n
# If you need to create an account, type (without the <>'s):
#      |wcreate <username> <password>|n
#
# If you have spaces in your username, enclose it in quotes.
# Enter |whelp|n for more info. |wlook|n will re-show this screen.
#|b==============================================================|n""" \
#    .format(settings.SERVERNAME, utils.get_evennia_version())
