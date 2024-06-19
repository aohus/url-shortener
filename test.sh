#!bin/bash
docker build -f Dockerfile.test -t test-image .
docker run --rm --name app-test test-image