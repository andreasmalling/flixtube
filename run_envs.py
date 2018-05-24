#!/usr/bin/python3
import datetime
from pathlib import Path
from subprocess import Popen
from time import sleep
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("stable_env", nargs='?', default="envs/default.env", help="set env of stable network. (Default: envs/default.env)")
parser.add_argument("-n", dest="runs", default=1, type=int, help="set # of runs per exp.")
args = parser.parse_args()

p = Path("envs/")


def main():
	for d in p.iterdir():
	    if d.is_dir():
	        print("Dir:", d)
	        for env in sorted(Path(d).iterdir()):
	            if env.with_suffix(".env"):
	            	for i in range(args.runs):
		                run_timestamp = datetime.datetime.now().isoformat('_')
		                print("\t", env, "\trun:", i+1, "\t", run_timestamp)
		                Path('data/logs/' + run_timestamp).mkdir(parents=True, exist_ok=True)
		                log = open("data/logs/" + run_timestamp + "/run.txt", "a")
		                cmd = ["python3", "./run.py", "-t", str(240), "-s", str(30), str(env), args.stable_env]
		                print("\t", *cmd,"\n")
		                Popen(cmd, stdout=log, stderr=log)
		                sleep(600)


if __name__ == "__main__":
    main()
