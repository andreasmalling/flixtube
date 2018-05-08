#! /bin/bash

DOCKER='true'
FILE=$(ls -t ./data/dump | head -1)

while getopts 'hlf:' flag; do
  case "${flag}" in
    h) echo "Help:"; echo -e "  -l\t Run locally"; echo -e "  -f\t Use alt file dump \n\t (Default: newest in data/dump)" ; exit 0 ;;
    l) DOCKER='false' ;;
    f) FILE="$(basename ${OPTARG})" ;;
    *) error "Unexpected option ${flag}" ;;
  esac
done

echo "Loading: $FILE"
echo ""

if $DOCKER; then
	echo "Running in Docker"
    docker-compose -f plot-compose.yml up -d --scale plot=0
    docker exec flixtube_mongo_1 mongorestore --drop --gzip --db flixtube_db --archive=/data/dump/$FILE
    docker exec -ti flixtube_mongo_1 mongo flixtube_db
else
	echo "Running Locally"
	mongorestore --drop --gzip --db flixtube_db --archive="$PWD/data/dump/$FILE"
	mongo flixtube_db
fi



