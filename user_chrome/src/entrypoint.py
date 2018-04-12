from time import sleep
import subprocess
from optparse import OptionParser
from enum import Enum

from User import User
from BingePersona import BingePersona
from IncognitoPersona import IncognitoPersona
from SkipperPersona import SkipperPersona
from IPFS import Ipfs


class PersonaType(Enum):
    BINGE = 1
    BINGELEAVE = 2
    INCOGNITO = 3
    INCOGNITOLEAVE = 4
    SKIPPER = 5
    SKIPPERLEAVE = 6

parser = OptionParser()
# Browser Options
parser.add_option("-m", "--manual", action="store_true", dest="manual", default=False)
parser.add_option("--head", action="store_true", dest="browserHead", default=False)

# IPFS Options
parser.add_option("--no-ipfs", action="store_false", dest="ipfsDaemon", default=True)
parser.add_option("-g", "--global-bootstrap", action="store_false", dest="ipfsLocal", default=True)

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
    user = User(options.browserHead)
    # Persona Behaviour
    hash = "QmUZTQDnKKwnjfKSfeezsD1YYL1efpNVLqriW4Lta64Tci"
    persona = None
    personaType = PersonaType.SKIPPERLEAVE # TODO get this from flag instead

    # switch case
    persona = {
        PersonaType.BINGE: BingePersona(user, hash),
        PersonaType.BINGELEAVE: BingePersona(user, hash, True),
        PersonaType.INCOGNITO: IncognitoPersona(user, hash),
        PersonaType.INCOGNITOLEAVE: IncognitoPersona(user, hash, True),
        PersonaType.SKIPPER: SkipperPersona(user, hash),
        PersonaType.SKIPPERLEAVE: SkipperPersona(user, hash, True)
    }[personaType]

    persona.act()
    persona.leave_website()
