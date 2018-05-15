#!/usr/bin/python3

import argparse
import datetime
import time
from subprocess import PIPE, Popen, TimeoutExpired
from pathlib import Path

default_env = Path.cwd() / "envs" / "default.env"
mongo_env = Path.cwd() / "envs" / "mongo.env"
compose_env_file = Path.cwd() / ".env"

run_timestamp = datetime.datetime.now().isoformat('_')

def main():
    setup_args()

    # setup data dirs
    Path('data/dump').mkdir(parents=True, exist_ok=True)
    Path('data/plot').mkdir(parents=True, exist_ok=True)
    Path('data/logs/' + run_timestamp).mkdir(parents=True, exist_ok=True)

    # Clean slate
    if args.clean:
        clean_db()
    stop_containers()

    scales = {}

    # Possible setup of stable network
    if args.env_stable_file is not None:
        print_title("SETUP OF STABLE NETWORK")

        scales = {**scales, **(import_scales(args.env_stable_file))}    # Merge dicts
        proc = run_containers(scales, "stable")
        try:
            proc.wait( args.setup_time )
        except TimeoutExpired:
            print("Timed out")
    
    # Run exp
    print_title("SETUP OF EXP. NETWORK")
    scales = {**scales, **(import_scales(args.env_exp_file))}    # Merge dicts
    proc = run_containers(scales, "exp")

    # Possible timeout of exp
    if args.timeout > 0:

        # Add network constraints
        time.sleep(4)   # Give docker compose a buffer for starting containers (Users have 5s busy wait)
        add_network_constraints(args.timeout + 30)  # 30 secs. buffer for bringing container setup down
        try:
            proc.wait( args.timeout )
        except TimeoutExpired:
            print("Timed out")

        stop_containers()
    else:
        try:
            proc.wait()
        except KeyboardInterrupt:
            pass
    # Plot results
    if args.plot:
        plot()

    # Export results
    if args.export:
        export()

    clean_exit()


def stop_containers():
    print_title("STOPPING ALL CONTAINERS")
    log = open("data/logs/" + run_timestamp + "/down.txt", "a")
    stop = Popen(["docker-compose", "down"], stdout=log, stderr=log)
    stop.wait()


def clean_db():
    print_title("DELETE FLiXTUBE DB")
    run_mongo()
    docker_exec("mongo",
                [ "mongo",
                  "flixtube_db",
                  "--eval", "db.dropDatabase()"])


def run_containers(scales, logname="0"):

    main_scale = [ "--scale", "bootstrap="  + scales.get("SCALE_BOOT", "0"),
                   "--scale", "host="       + scales.get("SCALE_HOST", "0"),
                   "--scale", "mongo="      + scales.get("SCALE_MONGO", "0"),
                   "--scale", "metric="     + scales.get("SCALE_METRIC", "0"),
                   "--scale", "network="    + scales.get("SCALE_NETWORK", "0"),
                   "--scale", "user_seed="  + scales.get("SCALE_SEED", "0"),
                   "--scale", "user_debug=" + scales.get("SCALE_DEBUG", "0")]

    user_scale = [ "--scale", "user_1="     + scales.get("SCALE_USER_1", "0"),
                   "--scale", "user_2="     + scales.get("SCALE_USER_2", "0"),
                   "--scale", "user_3="     + scales.get("SCALE_USER_3", "0"),
                   "--scale", "user_4="     + scales.get("SCALE_USER_4", "0"),
                   "--scale", "user_5="     + scales.get("SCALE_USER_5", "0"),
                   "--scale", "user_6="     + scales.get("SCALE_USER_6", "0")]

    log = open("data/logs/" + run_timestamp + "/scale_" + logname +".txt", "a")
    return Popen(["docker-compose", "up", "--no-recreate"] + main_scale + user_scale, stdout=log, stderr=log)


def setup_args():
    global args
    parser = argparse.ArgumentParser()

    parser.add_argument(dest="env_exp_file",
                        type=Path,
                        help="set env file for experiment")

    parser.add_argument(nargs="?",
                        dest="env_stable_file",
                        type=Path,
                        default=default_env,
                        help="set env file for stable network. (Default: " + str(default_env.relative_to(Path.cwd())) + ")")

    parser.add_argument("-s",
                        dest="setup_time",
                        type=int,
                        default="30",
                        help="set time given to start stable network, before invoking exp. (Default: 30 seconds)")

    parser.add_argument("-t",
                        dest="timeout",
                        type=int,
                        default="0",
                        help="set timeout of experiment in seconds")

    parser.add_argument("-e",
                        dest="export",
                        action="store_true",
                        default=False,
                        help="export results")

    parser.add_argument("--no-clean",
                        dest="clean",
                        action="store_false",
                        default=True,
                        help="don't clean db before or after run")

    parser.add_argument("--no-plot",
                        dest="plot",
                        action="store_false",
                        default=True,
                        help="don't plot the results")

    args = parser.parse_args()


def add_network_constraints(duration,
                            target="re2:user_([1-6]|seed|debug)_[0-9]*",
                            rate="20mbit"):
    print("Setting network at", rate, "for", target)
    log = open("data/logs/" + run_timestamp + "/pumba.txt", "a")
    Popen(["pumba", "netem", "--tc-image", "gaiadocker/iproute2", "--duration", str(duration) + "s", "rate", "--rate", rate, target], stdout=log, stderr=log)


def clean_env():
    if compose_env_file.exists():
        compose_env_file.unlink()


def docker_exec(container, command ):
    print("Executing", *command, "on", container)
    count = 0
    while True:
        log = open("data/logs/" + run_timestamp + "/exec.txt", "a")
        proc = Popen(["docker-compose", "exec"] + [container] + command, stdout=log, stderr=log )
        proc.communicate()

        if proc.returncode == 0 or count > 20:
            break
        else:
            count += 1
            print("Try:", count, "/ 20")
            time.sleep(1)

    return proc


def run_mongo():
    mongo_scale = import_scales(mongo_env)
    proc = run_containers(mongo_scale, "mongo")
    return proc


def export( filename=run_timestamp ):
    print_title("Export FLiXTUBE DB")
    run_mongo()
    docker_exec( "mongo",
                [ "mongodump",
                  "--db", "flixtube_db",
                  "--gzip",
                  "--archive=" + "/data/dump/" + filename + ".gz"])

    print("Export done.")

def clean_exit():
    # No such thing as too much cleaning!
    clean_env()

    if args.clean:
        clean_db()

    # Stop exp
    stop_containers()

    exit(0)

def import_scales(env_file):
    scales = {}

    # Create .env for docker-compose
    clean_env()
    compose_env_file.symlink_to(env_file)

    # Create dict of scales
    env_content = env_file.read_text().splitlines()
    for env in env_content:
        # Split lines beginning with SCALE
        if env.startswith("SCALE"):
            env_split = env.split("=", 1)
            scales[env_split.pop()] = env_split.pop()

    # Fail safe of if no scales found
    if scales == {}:
        print("No scales found in env:", env_file.name)
        clean_exit()
    else:
        print("Scales found in env:", env_file.name)
        for scale in scales:
            print(scale, ":\t", scales.get(scale))

    return scales


def plot():
    print_title("GENERATE PLOTS")
    log = open("data/logs/" + run_timestamp + "/plots.txt", "a")
    proc = Popen(["docker-compose", "--file", "plot-compose.yml", "run", "plot"], stdout=log, stderr=log)
    proc.wait()

def print_title(title):
    print('\033[95m# == ' + title + ' == #\033[0m')

if __name__ == "__main__":
    main()