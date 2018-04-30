#!/usr/bin/python3

import argparse
import datetime
import sys
from subprocess import PIPE, Popen, TimeoutExpired
from pathlib import Path

default_env = Path.cwd() / "envs" / "default.env"
mongo_env = Path.cwd() / "envs" / "mongo.env"
compose_env_file = Path.cwd() / ".env"


def main():
    setup_args()

    # Clean slate
    if args.clean:
        clean_db()
    stop_docker_compose()

    scales = {}

    # Possible setup of stable network
    if args.env_stable_file is not None:
        print("# == SETUP OF STABLE NETWORK == #")

        scales = {**scales, **(import_scales(args.env_stable_file))}    # Merge dicts
        proc = run_docker_compose(scales, run_users=False)
        try:
            proc.wait( args.setup_time )
        except TimeoutExpired:
            print("Timed out")
    
    # Run exp
    print("# == SETUP OF EXP. NETWORK == #")
    scales = {**scales, **(import_scales(args.env_exp_file))}    # Merge dicts
    proc = run_docker_compose(scales, run_users=True)

    # Possible timeout of exp
    if args.timeout > 0:
        try:
            proc.wait( args.timeout )
        except TimeoutExpired:
            print("Timed out")

        stop_docker_compose()

        # Plot results
        if args.plot:
            plot()

        # Export results
        if args.export:
            export()

    clean_exit()


def stop_docker_compose():
    stop = Popen(["docker-compose", "down"])
    stop.wait()


def clean_db():
    print("Deleting database.")
    run_mongo()
    proc = docker_exec("mongo",
                       [ "mongo",
                         "flixtube_db",
                         "--eval", "db.dropDatabase()"])
    proc.wait()


def query_yes_no():
    yes = {'yes', 'y'}
    no = {'no', 'n', ''}
    sys.stdout.write('\033[1m' + 'Please input [y/N]' + '\033[0m')
    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def run_docker_compose(scales, run_users=True):
    if not run_users:
        scales = dict((key, value) for key, value in scales.items() if not key.startswith("SCALE_USER"))

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

    return Popen(["docker-compose", "up"] + main_scale + user_scale, stdout=PIPE)


def setup_args():
    global args
    parser = argparse.ArgumentParser()

    parser.add_argument(dest="env_exp_file",
                        type=Path,
                        default=default_env,
                        help="set env file for experiment (Default: " + str(default_env.relative_to(Path.cwd())) + ")")

    parser.add_argument(nargs="?",
                        dest="env_stable_file",
                        type=Path,
                        help="set env file for stable network. If not set, only the experiment env will be used.")

    parser.add_argument("-s",
                        dest="setup_time",
                        type=int,
                        default="60",
                        help="set time given to start stable network, before invoking exp. (Default: 60 seconds)")

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

    parser.add_argument("-c",
                        dest="clean",
                        action="store_true",
                        default=False,
                        help="clean db before run")

    parser.add_argument("--no-plot",
                        dest="plot",
                        action="store_false",
                        default=True,
                        help="don't plot the results")

    args = parser.parse_args()


def clean_env():
    if compose_env_file.exists():
        compose_env_file.unlink()


def docker_exec(container, command ):
    return Popen(["docker-compose", "exec"] + [container] + command )


def run_mongo():
    mongo_scale = import_scales(mongo_env)
    return run_docker_compose(mongo_scale, False)


def export( filename=datetime.datetime.now().isoformat('_') ):
    print("Export mongo DB.")
    run_mongo()

    proc = docker_exec( "mongo",
                       [ "mongodump",
                         "--db", "flixtube_db",
                         "--gzip",
                         "--archive=" + "/data/dump/" + filename + ".gz"])
    proc.wait()

    print("Export done.")

def clean_exit():
    # No such thing as too much cleaning!
    clean_env()
    clean_db()

    # Stop exp
    stop_docker_compose()

    exit(0)

def import_scales(env_file):
    scales = {}

    # Clean Up env
    clean_env()

    # Create .env for docker-compose
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
        print("No scales found in env. Continue?")
        if query_yes_no():
            print("👌")
        else:
            clean_exit()
    else:
        print("Scales found in env:")
        for scale in scales:
            print(scale, ":\t", scales.get(scale))

    return scales


def plot():
    print("# === Plotting === #")
    proc = Popen(["docker-compose", "--file", "plot-compose.yml", "run", "plot"], stdout=PIPE)
    proc.communicate()
    proc.wait()


if __name__ == "__main__":
    main()