#! /bin/bash
EXPDIR=envs/leecher_percentage/
EXPENV=_experiment.env
STABLEENV=_stable.env

echo "Run exp. $EXPDIR"
for i in {10..60..10}
	do
		./run.py -e -s 160 -t 300 "$EXPDIR $i $EXPENV" "$EXPDIR $i $STABLEENV"
	done