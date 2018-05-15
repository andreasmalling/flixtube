#! /bin/bash
EXPDIR=envs/leecher_percentage/
EXPENV=_experiment.env
STABLEENV=_stable.env
TIMESETUP=160
TIMEEXP=300
TIMEBUFFER=120
SLEEP=$((TIMEEXP+TIMESETUP+$TIMEBUFFER))

echo "Run exp. $EXPDIR"
for i in {10..60..10}
	do
		echo "Percentage: $i"
		./run.py -e -s "$TIMESETUP" -t "$TIMEEXP" "$EXPDIR$i$EXPENV" "$EXPDIR$i$STABLEENV" &
		
		sleep "$SLEEP"s
	done