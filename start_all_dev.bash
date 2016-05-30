#!/bin/bash
inifile=$1
TIMEOUT=$2
#sed -i -e 's@gunicorn@waitress@' -e 's@worker.*@@' $inifile
sed -i -e 's@pyramid.includes =@pyramid.includes = pyramid_debugtoolbar@' $inifile
set -eo monitor
trap 'kill $(jobs -p) &> /dev/null' EXIT
trap 'exit 2' CHLD
./bin/runzeo -C etc/zeo.conf &
#./start_system.bash $inifile &
exec ./bin/gunicorn --access-logfile - --paste $inifile -t $TIMEOUT
#exec ./bin/pserve $inifile
