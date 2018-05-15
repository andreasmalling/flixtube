#!/usr/bin/env bash

LOG_RUN=run_envs.log
LOG_TS=run_envs_ts.log

timestamp(){
    echo -n "${1:- Timestamp} at "
    date +"%T"
}


run_envs_in(){
    for file in envs/"$1"/*; do
        timestamp "$file" | tee ${LOG_TS}
        ./run.py -e -t 240 -s 30 "$filename" envs/default.env 2>&1 | tee ${LOG_RUN} &
        sleep 600
    done
}

# Folders to run
declare -a arr=("binge"
                "incognito"
                "leecher"
                "skipper"
                )

touch "$LOG_RUN"
touch "$LOG_TS"


for i in "${arr[@]}"
do
    echo ========================
    timestamp "$i" | tee ${LOG_TS}
    echo ========================
    run_envs_in "$i"
done

