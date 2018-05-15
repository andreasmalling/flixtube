#!/bin/bash
USERS='re2:user_[1-6]_[0-9]*'
ALL_USERS='re2:user_([1-6]|seed|debug)_[0-9]*'
SEEDS="$ALL_USERS"

# docker pull gaiadocker/iproute2

slow_network() {
	echo Slow network: $1
	pumba netem --tc-image gaiadocker/iproute2 --duration 10m rate --rate $2 $1 &
	RATE_PID=$!
	printf "Slow PID:\t$RATE_PID\n"
}

late_network() {
	echo Late network: $1
	pumba netem --tc-image gaiadocker/iproute2 --duration 10m delay --time 40 --jitter 10 $1 &
	DELAY_PID=$!
	printf "Late PID:\t$DELAY_PID\n"
}

random_pause() {
	echo Random pause: $1
	pumba --random --interval 1s pause --duration 2s $1 &
}

handler()
{
    printf "\nKilling: $RATE_PID\n"
    kill -s SIGINT $RATE_PID
    exit 0
}

kill_pumba()
{
    printf "\nKilling: pumba\n"
	killall pumba
	exit 0
}

trap kill_pumba SIGINT

slow_network $SEEDS ${1:- 20mbit}

wait $RATE_PID