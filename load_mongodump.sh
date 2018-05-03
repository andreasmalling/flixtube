#! /bin/bash

if [ $# -eq 0 ]; then
	FILE=$(ls -t ./data/dump | head -1)
else
	FILE=$(basename $1)
fi

echo "Loading: $FILE"
echo ""

docker-compose -f plot-compose.yml up -d --scale plot=0
docker exec flixtube_mongo_1 mongorestore --drop --gzip --db flixtube_db --archive=/data/dump/$FILE
docker exec -ti flixtube_mongo_1 mongo flixtube_db