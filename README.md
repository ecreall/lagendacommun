# Getting Started for development

To execute all processes with docker:

    mkdir -p volumes/{arangodb,arangodb-apps} && sudo chown 999:999 volumes/{arangodb,arangodb-apps}
    ./run.sh rebuild
    ./run.sh

- To go through nginx and varnish: http://local.ecreall.com:8080
- To bypass nginx and go through varnish: http://local.ecreall.com:5000
- To bypass nginx and varnish: http://local.ecreall.com:5001

Connect with admin@example.com and password mybigsecret (defined in SECRET
environment variable in docker-compose-dev.yml)

To be able to send mail, open a tunnel and bind port 9025 to the docker bridge:

    ssh -L 172.17.0.1:9025:localhost:25 server_with_postfix.ecreall.com

To stop all containers:

    ./run.sh down

To run tests, example:

    ./run.sh test -s dace -t relations

# Production deployment (with docker-compose on the server)

    ./redeploy.sh

# zeopack

    docker exec lagendacommun_lac_1 /app/bin/zeopack -d 1 -u /app/var/zeo.sock

# How to get the logs

    docker logs -f --tail 200 lagendacommun_lac_1

