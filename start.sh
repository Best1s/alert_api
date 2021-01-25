#!/bin/bash
docker stop alert_api
docker rm alert_api
docker rmi alert_api
docker build -t alert_api:latest .
docker run -d -p 5000:5000 --name alert_api alert_api:latest
