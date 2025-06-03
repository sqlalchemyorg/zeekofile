import argparse
import logging
import os
import sys
import time
import traceback

from . import config
from . import server
from . import util
from .writer import _check_output
from .writer import _rebuild

logger = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--src-dir",
        dest="src_dir",
        help="Your site's source directory " "(default is current directory)",
        metavar="DIR",
        default=os.curdir,
    )
    parser.add_argument(
        "--serve",
        dest="serve",
        default=False,
        action="store_true",
        help="Serve built site via HTTP w/ refresh",
    )
    parser.add_argument(
        "--no-delete",
        dest="no_delete",
        default=False,
        action="store_true",
        help=(
            "when putting new files in _site, don't "
            "delete existing files / directories (but still overwrite "
            "specific files)"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        default=False,
        action="store_true",
        help="Be verbose",
    )
    parser.add_argument(
        "-vv",
        "--veryverbose",
        dest="veryverbose",
        default=False,
        action="store_true",
        help="Be extra verbose",
    )
    parser.add_argument(
        "PORT", nargs="?", default="8080", help="TCP port to use"
    )
    parser.add_argument(
        "IP_ADDR",
        nargs="?",
        default="127.0.0.1",
        help="IP address to bind to. Defaults to loopback only "
        "(127.0.0.1). 0.0.0.0 binds to all network interfaces, "
        "please be careful!",
    )
    args = parser.parse_args()
    return (parser, args)


def main(argv=None, **kwargs):
    parser, args = get_args()

    logging.basicConfig()

    if args.verbose:
        logging.getLogger("zeekofile").setLevel(logging.INFO)
        logger.info("Setting verbose mode")

    if args.veryverbose:
        logging.getLogger("zeekofile").setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")

    if not os.path.isdir(args.src_dir):
        print("source dir does not exist : %s" % args.src_dir)
        sys.exit(1)
    os.chdir(args.src_dir)

    sys.path.insert(0, os.curdir)

    config_init(args)

    output_dir = util.path_join("_site", util.fs_site_path_helper())

    if args.serve:
        print("Running an initial build")

    delete = not args.no_delete

    _rebuild(output_dir, delete)

    if args.serve:
        bfserver = server.Server(args.PORT, args.IP_ADDR)
        bfserver.start()
        state = {}
        while not bfserver.is_shutdown:
            try:
                time.sleep(0.5)
                _check_output(state, output_dir, delete)
            except KeyboardInterrupt:
                bfserver.shutdown()
            except:
                print(traceback.print_exc())


def config_init(args):
    try:
        config.init("_config.py")
    except config.ConfigNotFoundException:
        sys.exit(
            "No configuration found in source dir: {0}".format(args.src_dir)
        )


if __name__ == "__main__":
    main()
