from time import sleep
import subprocess
from optparse import OptionParser
from enum import Enum

from User import User
from BingePersona import BingePersona
from IPFS import Ipfs

class PersonaType(Enum):
    BINGE = 1

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
    hash = "some string"
    persona = None
    personaType = PersonaType.BINGE

    # switch case
    persona = {
        PersonaType.BINGE: BingePersona(user, hash)
    }[personaType]

    persona.act()

    # user.visit("http://host/webplayer.html")
    # user.watch_hash("QmdSuHL4rof1j5zv3iSoy7rxQc4kk6yNHcFxAKd9e1CeBs")
    # user.browser.find_option_by_text("Bitmovin (Adaptive)").first.click()