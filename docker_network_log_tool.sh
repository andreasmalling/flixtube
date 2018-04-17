#!/bin/bash

CONTAINER_ID=$1
STREAM=$2

IP=$(curl -X GET --unix-socket /var/run/docker.sock http:/v1.31/containers/$CONTAINER_ID/json | jq -c '.NetworkSettings.Networks.bridge.IPAddress')

echo $IP

curl -X GET --unix-socket /var/run/docker.sock http:/v1.31/containers/$CONTAINER_ID/stats?stream=$STREAM | jq "{ip: $IP, ts:.read, net:.networks.eth0}" >> network_$CONTAINER_ID.log
