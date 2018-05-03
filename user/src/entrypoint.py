#!/usr/bin/python3
import subprocess
import argparse
from enum import Enum, unique
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
    parser.set_defaults(video_hash="QmbVvwx8KidXo8Awr6GoF1QTrfkkuZsQjg33onkvwCf8ap")

    # Positional Arguments
    parser.add_argument('persona', type=PersonaType.from_string, choices=list(PersonaType))
    parser.add_argument('persona_options', metavar='OPTION', type=int, nargs='*',
                        help="options passed to PERSONA\n"
                             "BINGE: takes no arguments\n"
                             "INCOGNITO: takes 1 argument, how many seconds of the end of the video to watch\n"
                             "SKIPPER: takes 2 arguments, 1st is the skip length, 2nd is the watch length\n"
                             "IDLE: takes no arguments\n"
                             "LEECHER: takes no arguments")

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

    # Parse options
    args = parser.parse_args()

    # Handle Options
    if args.ipfs:
        ipfs = Ipfs()

        if args.ipfsLocal:
            ipfs.bootstrap_local()

        if args.ipfsSeed:
            ipfs.gateway_public()
            ipfs.add("/usr/src/app/video_dashed/")

        ipfs.run_daemon()

    if args.manual:
        subprocess.run(["google-chrome", "--no-first-run", "host/webplayer.html"])
    else:
        personaType = args.persona
        options = args.persona_options

        #Log persona type to database
        requests_retry_session().get('http://metric:8081/metrics/persona/' + personaType.name)

        user = User(args.browserHead)

        # Persona Behaviour
        hash = args.video_hash
        persona = None

        print(personaType)
        # switch case
        persona = {
            PersonaType.BINGE:      BingePersona(user, hash, args.leave_website, [0]),
            PersonaType.INCOGNITO:  IncognitoPersona(user, hash, args.leave_website, options),
            PersonaType.SKIPPER:    SkipperPersona(user, hash, args.leave_website, options),
            PersonaType.IDLE:       IdlePersona(user, hash, args.leave_website, options),
            personaType.LEECHER:    BingePersona(user, hash, args.leave_website, [1])
        }[personaType]
        persona.act()
        persona.leave_website()


# Src: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


if __name__ == '__main__':
    main()