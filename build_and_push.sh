#! /bin/bash
git pull
docker-compose build && docker-compose push
docker-compose -f plot-compose.yml build && docker-compose -f plot-compose.yml push