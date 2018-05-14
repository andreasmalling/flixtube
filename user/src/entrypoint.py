#!/usr/bin/python3
import subprocess
import argparse
from enum import Enum, unique
from time import sleep

import requests
from numpy.random import uniform as random
from retrying import retry
from User import User
from BingePersona import BingePersona
from IncognitoPersona import IncognitoPersona
from SkipperPersona import SkipperPersona
from IdlePersona import IdlePersona
from IPFS import Ipfs

@unique
class PersonaType(Enum):
    BINGE = 0
    INCOGNITO = 1
    SKIPPER = 2
    IDLE = 3
    LEECHER = 4
    SEEDER = 5

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return PersonaType[s]
        except KeyError:
            raise ValueError()

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    # Default options
    parser.set_defaults(video_hash="QmXMo4ZC2AQuR4Q2LCHi4uy6UQkGJFjxgfLMwhWZRu1iah",
                        random_delay=20)

    # Positional Arguments
    parser.add_argument('persona', type=PersonaType.from_string, choices=list(PersonaType))
    parser.add_argument('persona_options', metavar='OPTION', type=int, nargs='*',
                        help="options passed to PERSONA\n"
                             "BINGE: takes no arguments\n"
                             "INCOGNITO: takes 1 argument, how many seconds of the end of the video to watch\n"
                             "SKIPPER: takes 2 arguments, 1st is the skip length, 2nd is the watch length\n"
                             "IDLE: takes no arguments\n"
                             "LEECHER: takes no arguments\n"
                             "SEEDER: takes no arguments")

    # Browser Options
    parser.add_argument("-m", "--manual", action="store_true", dest="manual", default=False,
                        help="spawn browser for manual interaction")
    parser.add_argument("--head", action="store_false", dest="browserHead", default=True,
                        help="display browser while running persona")

    # IPFS Options
    parser.add_argument("--no-ipfs", action="store_false", dest="ipfs", default=True,
                        help="don't run ipfs daemon")
    parser.add_argument("-g", "--global", action="store_false", dest="ipfsLocal", default=True,
                        help="use default bootstrap for global access (Default: Local bootstrap")
    parser.add_argument("-s", "--seed", action="store_true", dest="ipfsSeed", default=False,
                        help="seeds content from folder videos_dashed in the IPFS network")

    # Persona options
    parser.add_argument("-l", "--leave", action="store_true", dest="leave_website", default=False,
                        help="makes persona leave IPFS network after finishing video (default False)")
    parser.add_argument("-v", "--video-hash", dest="video_hash",
                        help="set hash of video watched by persona")
    parser.add_argument("-r", type=int, dest="random_delay",
                        help="set max of random delay, before persona's action (Default: 20s)")

    # Parse options
    args = parser.parse_args()

    # Get Persona
    personaType = args.persona
    options = args.persona_options

    # Handle Options
    if args.ipfs or not personaType == PersonaType.LEECHER:
        ipfs = Ipfs()

        if args.ipfsLocal:
            ipfs.bootstrap_local()

        if args.ipfsSeed or personaType == PersonaType.SEEDER:
            print("Seeding...")
            ipfs.gateway_public()
            ipfs.add("/usr/src/app/video_dashed/")

        ipfs.run_daemon()

    if args.manual:
        subprocess.run(["google-chrome", "--no-first-run", "host/webplayer.html"])
    else:
        sleep( random() * args.random_delay )

        # Add persona with IP to db
        log_persona(personaType.name)

        # Persona Behaviour
        user = User(args.browserHead)
        hash = args.video_hash

        persona = {
            PersonaType.BINGE:      BingePersona(user, hash, args.leave_website, [0]),
            PersonaType.INCOGNITO:  IncognitoPersona(user, hash, args.leave_website, options),
            PersonaType.SKIPPER:    SkipperPersona(user, hash, args.leave_website, options),
            PersonaType.IDLE:       IdlePersona(user, hash, args.leave_website, options),
            personaType.LEECHER:    BingePersona(user, hash, args.leave_website, [1]),
            personaType.SEEDER:     IdlePersona(user, hash, args.leave_website, options)
        }[personaType]

        persona.act()

        persona.leave_website()


#Log persona type to database
@retry(wait_exponential_multiplier=100, wait_exponential_max=10000)
def log_persona(persona):
    print( "Logging Persona:", persona)
    return requests.get('http://metric:8081/metrics/persona/' + persona)


if __name__ == '__main__':
    main()