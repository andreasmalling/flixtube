#!/usr/bin/python3

import subprocess
from optparse import OptionParser, OptionGroup
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

persona_list = "PERSONA List:\t"
for pt in PersonaType:
    persona_list += str(pt.value) + "=" + pt.name + ", "
persona_list = persona_list[:-2] # Remove last comma

parser = OptionParser(usage="%prog [OPTIONS] PERSONA [PERSONA_ARGS]", description=persona_list)

# Browser Options
group_browser = OptionGroup(parser, "Browser Options")
group_browser.add_option("-m", "--manual", action="store_true", dest="manual", default=False,
                  help="spawn browser for manual interaction")
group_browser.add_option("--head", action="store_true", dest="browserHead", default=False,
                  help="display browser while running persona")
parser.add_option_group(group_browser)

# IPFS Options
group_ipfs = OptionGroup(parser, "IPFS Options")
group_ipfs.add_option("--no-ipfs", action="store_false", dest="ipfsDaemon", default=True,
                      help="don't run ipfs daemon")
group_ipfs.add_option("-g", "--global", action="store_false", dest="ipfsLocal", default=True,
                      help="use default bootstrap for global access (Default: Local bootstrap")
parser.add_option_group(group_ipfs)

# Persona options
group_persona = OptionGroup(parser, "Persona Options")
group_persona.add_option("-l", "--leave", action="store_true", dest="leave_website", default=False,
                  help="Makes persona leave IPFS network after finishing video (default False)")
parser.add_option_group(group_persona)

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

