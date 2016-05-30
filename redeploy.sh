#!/bin/bash
set -eo pipefail
REV="$1"
cd `dirname $0`
git config advice.detachedHead false
if [ -z "$REV" ]; then
  git checkout master
  git pull
else
  git fetch origin master
  git checkout "$REV"
fi

# mountpoints are not created automatically with docker >= 1.10
mkdir -p cache && chown 1000:1000 cache
mkdir -p var && chown 1000:1000 var
mkdir -p volumes/elasticsearch && chown 1000:1000 volumes/elasticsearch
mkdir -p volumes/{arangodb,arangodb-apps} && chown 999:999 volumes/{arangodb,arangodb-apps}
cp /home/deploy/.ssh/id_rsa /tmp/deploy_id_rsa
chmod o+r /tmp/deploy_id_rsa
options="-f docker-compose.yml" ./run.sh rebuild || rm -f /tmp/deploy_id_rsa
rm -f /tmp/deploy_id_rsa
docker-compose down
docker-compose up -d
