#!/bin/bash
project="alert_callback_api"
docker stop ${project} ||echo "not run ${project}"
docker rm ${project} || echo "not ${project} container"
docker rmi ${project} || echo "not ${project} images"
docker build -t ${project}:latest .
docker run -d -p 5000:5000 --name ${project} ${project}:latest