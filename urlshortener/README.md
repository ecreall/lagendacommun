# Pyster
A URL shortening Flask micro website similar to bit.ly 

To launch the application:

    docker build -t urlshortener .
    docker run -ti -p 5000:5000 -v /tmp/var:/app/var urlshortener

