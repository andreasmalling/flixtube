#!/usr/bin/python3

import subprocess
import argparse
from enum import Enum, unique

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

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return PersonaType[s]
        except KeyError:
            raise ValueError()


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

# Positional Arguments
parser.add_argument('persona', type=PersonaType.from_string, choices=list(PersonaType))
parser.add_argument('persona_options', metavar='OPTION', type=int, nargs='*',
                    help="options passed to PERSONA\n"
                         "BINGE: takes 1 argument (0 = don't leech, 1 = leech)\n"
                         "INCOGNITO: takes 1 argument, how many seconds of the end of the video to watch\n"
                         "SKIPPER: takes 2 arguments, 1st is the skip length, 2nd is the watch length\n"
                         "IDLE: takes no arguments")

# Browser Options
parser.add_argument("-m", "--manual", action="store_true", dest="manual", default=False,
                  help="spawn browser for manual interaction")
parser.add_argument("--head", action="store_true", dest="browserHead", default=False,
                  help="display browser while running persona")

# IPFS Options
parser.add_argument("--no-ipfs", action="store_false", dest="ipfsDaemon", default=True,
                      help="don't run ipfs daemon")
parser.add_argument("-g", "--global", action="store_false", dest="ipfsLocal", default=True,
                      help="use default bootstrap for global access (Default: Local bootstrap")

# Persona options
parser.add_argument("-l", "--leave", action="store_true", dest="leave_website", default=False,
                  help="makes persona leave IPFS network after finishing video (default False)")

# Parse options
args = parser.parse_args()

# Init IPFS
ipfs = Ipfs()

# Handle Options
if args.ipfsLocal:
    ipfs.bootstrap_local()

if args.ipfsDaemon:
    ipfs.run_daemon()

if args.manual:
    subprocess.run(["google-chrome", "--no-first-run", "host/webplayer.html"])
else:
    personaType = args.persona
    options = args.persona_options

    user = User(args.browserHead)

    # Persona Behaviour
    hash = "QmNsdjY3GoRbubyAeR8ZimTCCp8v11ryhJxfe9hqngRRCc"
    persona = None

    print(personaType)
    # switch case
    persona = {
        PersonaType.BINGE: BingePersona(user, hash, args.leave_website, options),
        PersonaType.INCOGNITO: IncognitoPersona(user, hash, args.leave_website, options),
        PersonaType.SKIPPER: SkipperPersona(user, hash, args.leave_website, options),
        PersonaType.IDLE: IdlePersona(user, hash, args.leave_website, options)
    }[personaType]
    persona.act()
    persona.leave_website()
