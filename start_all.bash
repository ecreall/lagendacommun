#!/bin/bash
inifile=$1
TIMEOUT=$2
exec ./codep \
    './bin/runzeo -C etc/zeo.conf' \
    "./bin/gunicorn --access-logfile - --paste $inifile -t $TIMEOUT" \
    "./start_system.bash $inifile"
