#!/bin/bash

CONTAINER_ID=${1:- flixtube_user_1_1}
STREAM=${2:- false}

IP=$(curl -X GET --unix-socket /var/run/docker.sock http:/v1.31/containers/$CONTAINER_ID/json | jq -c '.NetworkSettings.Networks.bridge.IPAddress')

echo $IP

curl -X GET --unix-socket /var/run/docker.sock http:/v1.31/containers/$CONTAINER_ID/stats?stream=$STREAM | jq . >> network_$CONTAINER_ID.log # "{ip: $IP, ts:.read, net:.networks.eth0}" >> network_$CONTAINER_ID.log
