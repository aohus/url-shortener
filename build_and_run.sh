#!bin/bash
docker build -t fastapi-url-shortener .
docker run --rm -p 8000:8000 --name url-shortner fastapi-url-shortener