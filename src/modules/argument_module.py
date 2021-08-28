"""
this module loads user-customizable default arguments
"""

import os
from argparse import ArgumentParser

parser = ArgumentParser(description="freiefreiburgdaten")
parser.add_argument("-f", "--file",
                    help="custom meta.json file",
                    metavar="FILE",
                    type=str)
parser.add_argument("-m", "--mapbox-api",
                    help="mapbox api toke",
                    metavar="MAPBOX API",
                    type=str)
parser.add_argument("-s", "--mapbox-style",
                    help="mapbox api style token",
                    metavar="MAPBOX API",
                    type=str)
parser.add_argument(
    '--debug',
    action='store_true',
    default=False,
    help='enable debug mode'
)

cmd_args = parser.parse_args()

DEBUG = cmd_args.debug or bool(os.environ.get('DASH_DEBUG', True))
META_JSON = cmd_args.file or os.environ.get('DASH_META_JSON', False) or "data/meta.json"
MAPBOX_API = {
    "style": cmd_args.mapbox_style or
             os.environ.get('DASH_MAPBOX_STYLE', False) or
             "mapbox://styles/valentinkolb/cksjew54g1s4t18s063qaku5k",
    "token": cmd_args.mapbox_api or
             os.environ.get('DASH_MAPBOX_API', False) or
             "pk.eyJ1IjoidmFsZW50aW5rb2xiIiwiYSI6ImNrczdtb3ZvNzFlbHQycHBobDFzN2RjMXAifQ.yp1dgX8hJcZM1r9Tq7eW2A"
}
