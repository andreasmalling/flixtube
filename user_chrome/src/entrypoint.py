from time import sleep
import subprocess
from optparse import OptionParser
from enum import Enum

import sys

from User import User
from BingePersona import BingePersona
from IncognitoPersona import IncognitoPersona
from SkipperPersona import SkipperPersona
from IPFS import Ipfs


class PersonaType(Enum):
    BINGE = 0
    INCOGNITO = 1
    SKIPPER = 2

parser = OptionParser()
# Browser Options
parser.add_option("-m", "--manual", action="store_true", dest="manual", default=False)
parser.add_option("--head", action="store_true", dest="browserHead", default=False)

# IPFS Options
parser.add_option("--no-ipfs", action="store_false", dest="ipfsDaemon", default=True)
parser.add_option("-g", "--global-bootstrap", action="store_false", dest="ipfsLocal", default=True)

# Persona options
parser.add_option("-l", "--leave", action="store_true", dest="leave_website", default=False,
                  help="Makes persona leave IPFS network after finishing video (default False)")

# Parse options
(options, args) = parser.parse_args()

# Init IPFS
ipfs = Ipfs()

# Handle Options
if options.ipfsLocal:
    ipfs.bootstrap_local()

if options.ipfsDaemon:
    ipfs.run_daemon()

if options.manual:
    subprocess.run(["google-chrome", "--no-first-run", "host/webplayer.html"])
else:
    if len(args) < 1:
        print("persona number must be specified")
        sys.exit(0)
    personaType = int(args[0])
    values = [item.value for item in PersonaType]
    if personaType not in values:
        print("not a valid persona")
        sys.exit(0)
    args.remove(args[0])

    user = User(options.browserHead)

    # Persona Behaviour
    hash = "QmNsdjY3GoRbubyAeR8ZimTCCp8v11ryhJxfe9hqngRRCc"
    persona = None

    # switch case
    persona = {
        PersonaType.BINGE.value: BingePersona(user, hash, options.leave_website, args),
        PersonaType.INCOGNITO.value: IncognitoPersona(user, hash, options.leave_website, args),
        PersonaType.SKIPPER.value: SkipperPersona(user, hash, options.leave_website, args)
    }[personaType]
    persona.act()
    persona.leave_website()

