import logging
import os
import sys
import traceback
import time
import argparse

from . import config, site_init, util, server, cache, filter, controller


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src-dir", dest="src_dir",
                        help="Your site's source directory "
                                 "(default is current directory)",
                        metavar="DIR", default=os.curdir)
    parser.add_argument("-v", "--verbose", dest="verbose",
                                 default=False, action="store_true",
                                 help="Be verbose")
    parser.add_argument("-vv", "--veryverbose", dest="veryverbose",
                                 default=False, action="store_true",
                                 help="Be extra verbose")
    parser.add_argument("PORT", nargs="?", default="8080",
                         help="TCP port to use")
    parser.add_argument("IP_ADDR", nargs="?", default="127.0.0.1",
                         help="IP address to bind to. Defaults to loopback only "
                         "(127.0.0.1). 0.0.0.0 binds to all network interfaces, "
                         "please be careful!")
    args = parser.parse_args()
    return (parser, args)


def main(argv=None, **kwargs):
    parser, args = get_args()

    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info("Setting verbose mode")

    if args.veryverbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")

    if not os.path.isdir(args.src_dir):
        print("source dir does not exist : %s" % args.src_dir)
        sys.exit(1)
    os.chdir(args.src_dir)

    sys.path.insert(0, os.curdir)

    config_init(args)

    global output_dir
    output_dir = util.path_join("_site", util.fs_site_path_helper())

    print ("Running an initial build")
    _rebuild()

    bfserver = server.Server(args.PORT, args.IP_ADDR)
    bfserver.start()
    state = {}
    while not bfserver.is_shutdown:
        try:
            time.sleep(.5)
            _check_output(state)
        except KeyboardInterrupt:
            bfserver.shutdown()
        except:
            print traceback.print_exc()


def config_init(args):
    try:
        config.init("_config.py")
    except config.ConfigNotFoundException:
        sys.exit("No configuration found in source dir: {0}".format(args.src_dir))


if __name__ == "__main__":
    main()
