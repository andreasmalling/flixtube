#!/usr/bin/env sh
CONTAINER=flixtube_mongo_1
DB_NAME=flixtube_db
EXP_DATE=$(date '+%Y-%m-%d_%H:%M:%S')
EXP_NAME=/data/dump/"$EXP_DATE"_"${1:-exp0}".gz

echo "DATE: $EXP_DATE"
# Spin up mongo
bash ./run.sh envs/mongo.env &

sleep 10

# Export DB as archieved binary
docker exec $CONTAINER mongodump --db $DB_NAME --gzip --archive=$EXP_NAME

# Drop database, for next experiment
docker exec $CONTAINER mongo $DB_NAME --eval "db.dropDatabase()"

# Spin down mongo
while [ ! -f ".$EXP_NAME" ]
do
    echo Sleeping...
    sleep 2
done
docker-compose down