import argparse
import sys
from subprocess import PIPE, Popen, TimeoutExpired
from pathlib import Path

def run_docker_compose() :
    options = ["--scale", "bootstrap="  + scales.get("SCALE_BOOT", "1"),
               "--scale", "host="       + scales.get("SCALE_HOST", "1"),
               "--scale", "mongo="      + scales.get("SCALE_MONGO", "1"),
               "--scale", "metric="     + scales.get("SCALE_METRIC", "1"),
               "--scale", "network="    + scales.get("SCALE_NETWORK", "1"),
               "--scale", "user_seed="  + scales.get("SCALE_SEED", "1"),
               "--scale", "user_debug=" + scales.get("SCALE_DEBUG", "0"),
               "--scale", "user_1="     + scales.get("SCALE_USER_1", "0"),
               "--scale", "user_2="     + scales.get("SCALE_USER_2", "0"),
               "--scale", "user_3="     + scales.get("SCALE_USER_3", "0"),
               "--scale", "user_4="     + scales.get("SCALE_USER_4", "0"),
               "--scale", "user_5="     + scales.get("SCALE_USER_5", "0"),
               "--scale", "user_6="     + scales.get("SCALE_USER_6", "0")]


    proc = Popen(["docker-compose", "up"] + options, stdout=PIPE)
    if args.timeout > 0:
        try:
            outs, errs = proc.communicate(timeout=args.timeout)
        except TimeoutExpired:
            print("Timed out after:", args.timeout)
            proc.send_signal(2)
    outs, errs = proc.communicate()

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

# Setup options
parser = argparse.ArgumentParser()
parser.add_argument(nargs="?", dest="env_file", type=Path, default="./envs/default.env",
                    help="set env file [Default: ./envs/default.env]")

parser.add_argument("-t", dest="timeout", type=int, default="0",
                    help="set timeout")
args = parser.parse_args()

# Get environment file
env_file = Path.cwd() / args.env_file

# Create .env for docker-compose
compose_env_file = Path.cwd() / ".env"

if compose_env_file.exists():
    compose_env_file.unlink() # Clean up

compose_env_file.symlink_to( env_file )

# Create dict of scales
env_content = env_file.read_text().splitlines()
scales ={}
for env in env_content:
    # Ignore comments
    if env[0] == "#" :
        continue
    # Split assignments
    env_split = env.split("=", 1)
    if env_split[0].startswith("SCALE"):
        scales[env_split.pop()] = env_split.pop()

# Fail safe of if no scales found
if scales == {}:
    print("No scales found in env")
    if query_yes_no():
        print("👌")
    else:
        compose_env_file.unlink() # Clean up
        exit(0)
else:
    print("Scales found in env:")
    for scale in scales:
        print(scale, ":\t", scales.get(scale))

run_docker_compose()

if compose_env_file.exists():
    compose_env_file.unlink() # Clean up