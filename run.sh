#!/usr/bin/env sh
ARG_ENV=${1:-envs/default.env}
COMPOSE_ENV=.env
SCALES=$(cat $ARG_ENV | grep -e ^SCALE)

clean_env() {
    echo "Cleaning up environment"
    ## Removes .env file variables from shell environment
    unset $(cat $ARG_ENV | grep -e ^SCALE | sed -E 's/(.*)=.*/\1/' | xargs)
    rm -f $COMPOSE_ENV
}

run_docker_compose() {
    docker-compose up 							\
        --scale bootstrap=${SCALE_BOOT:-1}		\
        --scale host=${SCALE_HOST:-1}  			\
        --scale mongo=${SCALE_MONGO:-1} 		\
        --scale metric=${SCALE_METRIC:-1} 		\
        --scale network=${SCALE_NETWORK:-1} 	\
        --scale user_seed=${SCALE_SEED:-1} 		\
        --scale user_debug=${SCALE_DEBUG:-0} 	\
        --scale user_1=${SCALE_USER_1:-0} 		\
        --scale user_2=${SCALE_USER_2:-0} 		\
        --scale user_3=${SCALE_USER_3:-0} 	    \
        --scale user_4=${SCALE_USER_4:-0} 	    \
        --scale user_5=${SCALE_USER_5:-0} 	    \
        --scale user_6=${SCALE_USER_6:-0}       \
        --force-recreate
}

# Grab ctrl-c for cleanup
trap "clean_env" INT

# Check if scales are set in supplied .env file
if [ -n "$SCALES" ]; then
    echo "\nScales found from environment file:" $ARG_ENV
    echo "$SCALES\n"

    # Sets scales for run_docker_compose function
    export $(cat $ARG_ENV | grep -e ^SCALE | xargs)
else
    echo "No scales found in" $ARG_ENV
    read -p "Continue (y/n)?" choice
    case "$choice" in
        y|Y ) echo "👌";;
        n|N ) exit 0;;
        * ) echo "invalid";;
    esac
fi

# Creates .env for docker-compose file
cp --force $ARG_ENV $COMPOSE_ENV

# Run the docker-compose command
run_docker_compose

# Clean up
clean_env