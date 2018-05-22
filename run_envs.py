#!/usr/bin/python3
import datetime
from pathlib import Path
from subprocess import Popen
from time import sleep

p = Path("envs/")

for d in p.iterdir():
    if d.is_dir():
        print("Dir:", d)
        for env in d.iterdir():
            if env.with_suffix(".env"):
                run_timestamp = datetime.datetime.now().isoformat('_')
                print(run_timestamp, env)
                Path('data/logs/' + run_timestamp).mkdir(parents=True, exist_ok=True)
                log = open("data/logs/" + run_timestamp + "/run.txt", "a")
                cmd = ["python3", "./run.py", "-t", str(240), "-s", str(30), str(env), "envs/default.env"]
                print(*cmd)
                Popen(cmd, stdout=log, stderr=log)
                sleep( 600 )