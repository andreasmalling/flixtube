#!/bin/bash
USERS='re2:user_[1-6]_[0-9]*'
ALL_USERS='re2:user_([1-6]|seed|debug)_[0-9]*'
CONTAINERS="$ALL_USERS"

TCIMG=gaiadocker/iproute2
DURATION=10m


# Chech for tc image
if [[ "$(docker images -q $TCIMG 2> /dev/null)" == "" ]]; then
	printf "Missing image: $TCIMG\n"
	docker pull $TCIMG
fi


slow_network() {
	echo Slow network: $1
	pumba netem --tc-image $TCIMG --duration $DURATION rate --rate $2 $1 &
	RATE_PID=$!
	printf "Slow PID:\t$RATE_PID\n"
}


late_network() {
	echo Late network: $1
	pumba netem --tc-image $TCIMG --duration $DURATION delay --time 40 --jitter 10 $1 &
	DELAY_PID=$!
	printf "Late PID:\t$DELAY_PID\n"
}


random_pause() {
	echo Random pause: $1
	pumba --random --interval 10s pause --duration $DURATION $1 &
	PAUSE_PID=$!
	printf "Pause PID:\t$DELAY_PID\n"
}


kill_pumba()
{
    printf "\nKilling: pumba\n"
	killall pumba
	exit 0
}
trap kill_pumba SIGINT

slow_network $CONTAINERS ${1:- 20mbit}
wait $RATE_PID