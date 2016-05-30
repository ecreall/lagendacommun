#!/bin/bash
# To generate CREDENTIALS:
# $ python
# >>> import base64
# >>> base64.encodestring('admin:password')[:-1]
# 'dXNlcm5hbWU6cGFzc3dvcmQ='
#
# To execute the script:
# docker exec www.lagendacommun.com /app/services/import_entities.sh "dXNlcm5hbWU6cGFzc3dvcmQ="

SERVER="${SERVER:-127.0.0.1:5002}"
CREDENTIALS=$1
APP_DIR=${APP_DIR:-/app}

JSON_FILE="${JSON_FILE:-file:////app/var/entities.json}"
URL="http://$SERVER/@@import_url"
python3.4 $APP_DIR/services/services_caller.py -t $JSON_FILE -c cultural_event
curl --silent --show-error --fail --insecure -o /dev/null -X POST -d "source=$JSON_FILE" $URL -H "Authorization: Basic ${CREDENTIALS}"
