#!/usr/bin/python3

import argparse
import datetime
import time
from subprocess import Popen, TimeoutExpired
from pathlib import Path

default_env = Path.cwd() / "envs" / "default.env"
mongo_env = Path.cwd() / "envs" / "mongo.env"
compose_env_file = Path.cwd() / ".env"

run_timestamp = datetime.datetime.now().isoformat('_')


def main():
    # Parse run options
    setup_args()

    # Setup data dirs
    Path('data/dump').mkdir(parents=True, exist_ok=True)
    Path('data/plot').mkdir(parents=True, exist_ok=True)
    Path('data/logs/' + run_timestamp).mkdir(parents=True, exist_ok=True)

    # Clean slate
    clean_up()

    scales = {}

    # Possible setup of stable network
    if args.env_stable_file is not None:
        print_title("SETUP OF STABLE NETWORK")

        scales = {**scales, **(import_scales(args.env_stable_file))}    # Merge dicts
        proc = run_containers(scales, "stable")
        try:
            proc.wait(args.setup_time)
        except TimeoutExpired:
            print("Timed out")

    # Run exp
    print_title("SETUP OF EXP. NETWORK")
    scales = {**scales, **(import_scales(args.env_exp_file))}    # Merge dicts
    proc = run_containers(scales, "exp")

    # Add network constraints
    time.sleep(4)   # Give docker compose a buffer for starting all containers (Users have 5s busy wait)

    if args.net_rate != 0:
        add_network_rate(args.exp_time + 30, rate=args.net_rate)  # 30 secs. buffer for bringing container setup down

    if args.net_latency is not None:
        add_network_latency(args.exp_time + 30, delay=args.net_latency)   # 30 secs. buffer again

    # Timeout of exp
    if args.exp_time > 0:
        try:
            proc.wait(args.exp_time)
        except TimeoutExpired:
            print("Timed out")

        stop_containers()
    else:   # or run until killed
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

    clean_up()
    exit(0)


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
                        help="set env file for stable network. (Default: " +
                             str(default_env.relative_to(Path.cwd())) + ")")

    parser.add_argument("-s",
                        dest="setup_time",
                        type=int,
                        default="30",
                        help="set time given to start stable network, before invoking exp. (Default: 30 seconds)")

    parser.add_argument("-t",
                        dest="exp_time",
                        type=int,
                        default="0",
                        help="set timeout of experiment in seconds")

    parser.add_argument("-l",
                        type=int,
                        dest="net_latency",
                        help="add latency in ms to all users.")

    parser.add_argument("-r",
                        dest="net_rate",
                        default="20mbit",
                        help="add data rate for all users. Suffix with [g|m|k]bit")

    parser.add_argument("--no-export",
                        dest="export",
                        action="store_false",
                        default=True,
                        help="don't export the results")

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

    log = open("data/logs/" + run_timestamp + "/scale_" + logname + ".txt", "a")
    return Popen(["docker-compose", "up", "--no-recreate"] + main_scale + user_scale, stdout=log, stderr=log)


def stop_containers():
    print_title("STOPPING ALL CONTAINERS")
    log = open("data/logs/" + run_timestamp + "/down.txt", "a")
    stop = Popen(["docker-compose", "down"], stdout=log, stderr=log)
    stop.wait()


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
        clean_up()
        exit(0)
    else:
        print("Scales found in env:", env_file.name)
        for scale in scales:
            print(scale, ":\t", scales.get(scale))

    return scales


def add_network_rate(duration,
                     rate,
                     target="re2:user_([1-6]|seed|debug)_[0-9]*"):
    print("Setting network at", rate, "for", target)
    log = open("data/logs/" + run_timestamp + "/pumba_rate.txt", "a")
    Popen(["pumba",
           "netem",
           "--tc-image", "gaiadocker/iproute2",
           "--duration", str(duration) + "s",
           "rate",
           "--rate", rate,
           target], stdout=log, stderr=log)


def add_network_latency(duration,
                        delay,
                        jitter=10,
                        target="re2:user_([1-6]|seed|debug)_[0-9]*"):
    print("Setting network latency at", delay, "+/-", jitter, "for", target)
    log = open("data/logs/" + run_timestamp + "/pumba_latency.txt", "a")
    Popen(["pumba",
           "netem",
           "--tc-image", "gaiadocker/iproute2",
           "--duration", str(duration) + "s",
           "delay",
           "--time", str(delay),
           "--jitter", str(jitter),
           target], stdout=log, stderr=log)


def docker_exec(container, command):
    count = 0
    log = open("data/logs/" + run_timestamp + "/exec.txt", "a")
    while True:
        print("Executing", *command, "on", container)
        proc = Popen(["docker-compose", "exec"] + [container] + command, stdout=log, stderr=log)
        proc.communicate()

        if proc.returncode == 0 or count > 20:
            break
        else:
            count += 1
            print("Try:", count, "/ 20 failed due to exit code", proc.returncode)
            time.sleep(1)

    return proc


def run_db():
    mongo_scale = import_scales(mongo_env)
    proc = run_containers(mongo_scale, "mongo")
    return proc


def clean_env():
    if compose_env_file.exists():
        compose_env_file.unlink()


def clean_db():
    print_title("DELETE FLiXTUBE DB")
    run_db()
    docker_exec("mongo",
                ["mongo",
                 "flixtube_db",
                 "--eval", "db.dropDatabase()"])


def clean_up():
    # No such thing as too much cleaning!
    clean_env()

    if args.clean:
        clean_db()

    # Stop exp
    stop_containers()


def plot():
    print_title("GENERATE PLOTS")
    log = open("data/logs/" + run_timestamp + "/plots.txt", "a")
    proc = Popen(["docker-compose", "--file", "plot-compose.yml", "run", "plot"], stdout=log, stderr=log)
    proc.wait()


def export(filename=run_timestamp):
    print_title("Export FLiXTUBE DB")
    run_db()
    docker_exec("mongo",
                ["mongodump",
                 "--db", "flixtube_db",
                 "--gzip",
                 "--archive=" + "/data/dump/" + filename + ".gz"])

    print("Export done.")


def print_title(title):
    print('\033[95m# == ' + title + ' == #\033[0m')


if __name__ == "__main__":
    main()
