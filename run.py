#!/usr/bin/python3

import argparse
import sys
from subprocess import PIPE, Popen, TimeoutExpired
from pathlib import Path

default_env = Path.cwd() / "envs" / "default.env"
mongo_env =  Path.cwd() / "envs" / "mongo.env"
compose_env_file = Path.cwd() / ".env"

def stop_docker_compose() :
    stop = Popen(["docker-compose", "down"])
    stop.wait()

def run_docker_compose(scales, run_users=True) :
    if not run_users:
        scales = dict((key, value) for key, value in scales.items() if not key.startswith("SCALE_USER"))

    main_scale = [ "--scale", "bootstrap="  + scales.get("SCALE_BOOT", "1"),
                   "--scale", "host="       + scales.get("SCALE_HOST", "1"),
                   "--scale", "mongo="      + scales.get("SCALE_MONGO", "1"),
                   "--scale", "metric="     + scales.get("SCALE_METRIC", "1"),
                   "--scale", "network="    + scales.get("SCALE_NETWORK", "1"),
                   "--scale", "user_seed="  + scales.get("SCALE_SEED", "1"),
                   "--scale", "user_debug=" + scales.get("SCALE_DEBUG", "0")]

    user_scale = [ "--scale", "user_1="     + scales.get("SCALE_USER_1", "0"),
                   "--scale", "user_2="     + scales.get("SCALE_USER_2", "0"),
                   "--scale", "user_3="     + scales.get("SCALE_USER_3", "0"),
                   "--scale", "user_4="     + scales.get("SCALE_USER_4", "0"),
                   "--scale", "user_5="     + scales.get("SCALE_USER_5", "0"),
                   "--scale", "user_6="     + scales.get("SCALE_USER_6", "0")]

    return Popen(["docker-compose", "up"] + main_scale + user_scale, stdout=PIPE)


def set_timeout(proc, timeout, func=None) :
    try:
        outs, errs = proc.communicate(timeout=timeout)
    except TimeoutExpired :
        if func is None :
            print("Timed out after", timeout, "seconds.")
        else :
            func()


def query_yes_no() :
    yes = {'yes','y'}
    no = {'no','n', ''}
    sys.stdout.write("Continue? [y/N]")
    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


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
                        help="set time given to create stable network, before invoking experiment. (Default: 60 seconds)")

    parser.add_argument("-t",
                        dest="timeout",
                        type=int,
                        default="0",
                        help="set timeout of experiment in seconds")

    parser.add_argument("-e",
                        dest="export",
                        action="store_true",
                        default="false",
                        help="export results")

    args = parser.parse_args()


def clean_env() :
    if compose_env_file.exists():
        compose_env_file.unlink()


def export() :
    print("Keeping mongo alive")
    clean_env()
    mongo_scale = import_scales(mongo_env)
    proc = run_docker_compose(mongo_scale, False)
    # TODO: Add export from mongo + plotting?


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
        print("No scales found in env")
        if query_yes_no():
            print("👌")
        else:
            compose_env_file.unlink()  # Clean up
            exit(0)
    else:
        print("Scales found in env:")
        for scale in scales:
            print(scale, ":\t", scales.get(scale))

    return scales


def main() :
    setup_args()

    # Clean slate
    stop_docker_compose()

    # Possible setup of stable network
    if args.env_stable_file is not None:
        print("# == SETUP OF STABLE NETWORK == #")

        main_scales = import_scales(args.env_stable_file)
        proc = run_docker_compose(main_scales, run_users=False)

        set_timeout(proc, args.setup_time )

    # Run exp
    print("# == SETUP OF EXP. NETWORK == #")
    exp_scales = import_scales(args.env_exp_file)
    proc = run_docker_compose(exp_scales, run_users=True)

    # Possible timeout of exp
    if args.timeout > 0:
        set_timeout(proc, args.timeout )

    # Export results
    if args.export:
        export()
    else:
        stop_docker_compose()


if __name__ == "__main__":
    main()