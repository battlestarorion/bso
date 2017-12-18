#!/bin/bash
# Must be run from root project directory and performed after the repositories are setup on the server.
SECRET_SETTINGS=$(pwd)/server/conf/secret_settings.py
SERVER_ROOT=/var/telnet
SECRET_SETTINGS_DEST=server/conf/secret_settings.py

scp $SECRET_SETTINGS $USER@thecryingbeard.com:$SERVER_ROOT/thecryingbeard.com/$SECRET_SETTINGS_DEST
scp $SECRET_SETTINGS $USER@thecryingbeard.com:$SERVER_ROOT/staging.thecryingbeard.com/$SECRET_SETTINGS_DEST
