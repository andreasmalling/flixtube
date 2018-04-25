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

# wait for export
while [ ! -f ".$EXP_NAME" ]
do
    echo -n "Sleeping"
    sleep 1
    echo -e "\e[0K\r Sleeping."
    sleep 1
done

# Drop database, for next experiment
docker exec $CONTAINER mongo $DB_NAME --eval "db.dropDatabase()"

# Spin down container
docker-compose down
