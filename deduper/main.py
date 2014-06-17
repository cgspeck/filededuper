#!/usr/bin/env python
# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE file.
import argparse
import datetime
import time
import signal
import logging
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import scanfiles
from . import models
from . import printpopularitylist
from . import dedupeselector


def connect_to_db(URI):
    engine = create_engine(URI, echo=False)
    Session = sessionmaker(bind=engine)
    return engine, Session()


def setup_logging():    # pragma: no cover
    log_format = '%(asctime)s:%(levelname)s:%(filename)s(%(lineno)d) ' \
        '%(message)s'
    log_level = logging.DEBUG
    logging.basicConfig(format=log_format, level=log_level)


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    insp = frame
    i = 500
    while True:
        if 'session' in insp.f_locals:
            print('Closing database')
            insp.f_locals['session'].close()
            sys.exit()
        else:
            if i < 0:
                print('Could not cleanly close database session')
                break
            else:
                insp = frame.f_back
            i -= 1
    sys.exit(0)


def silly_function():
    while True:
        print(datetime.datetime.now())
        time.sleep(1)


def main():  # pragma: no cover
    setup_logging()
    signal.signal(signal.SIGINT, signal_handler)
    default_db = 'sqlite:///files.db'
    parser = argparse.ArgumentParser(description='This application is subject '
    'to the revised 3-clause BSD license, as set out in the LICENSE  file '
    'found in the top-level directory of this distribution. USE AT YOUR OWN '
    'RISK AND ONLY AFTER TAKING A BACKUP. RUNNING IN DEDUPE MODE MAY ERASE '
    'NON-SELECTED FILES.')
    function_group = parser.add_mutually_exclusive_group()
    function_group.add_argument(
        '--scan', '-s', action='store_true',
        help='Scan given folder for image files and store hash')
    function_group.add_argument(
        '--printlist', '-p', choices=['csv', 'json'],
        help='Print duplicate count, suggestion (csv) and file list (json)')
    function_group.add_argument(
        '--dedupe', '-d', choices=['auto', 'graphical', 'cli'],
        help='Interactively prompt to delete duplicate files')
    parser.add_argument('--db', default=default_db,
        help='Database URI, e.g. {0}'.format(default_db))
    parser.add_argument('folder', nargs='?', default=os.getcwd(),
        help='Folder to scan')
    parser.add_argument(
        '--suggest_mode', choices=['longest_name', 'shortest_name'],
        help='Mode in which to suggest files', default='shortest_name')
    parser.add_argument(
        '--delete', action='store_true',
        help='Do not hardlink duplicate files, just delete them')

    args = parser.parse_args()

    if not (args.printlist or args.dedupe or args.scan):
        parser.print_help()

    engine, session = connect_to_db(args.db)
    models.create_tables(engine)

    if args.printlist:
        printpopularitylist.PrintPopularityList(session,
            print_mode=args.printlist, suggest_mode=args.suggest_mode)
    elif args.dedupe:
        dedupeselector.Dedupe(session, suggest_mode=args.suggest_mode,
            runmode=args.dedupe, link=not(args.delete))
    elif args.scan:
        if os.path.isdir(args.folder):
            scanfiles.ScanFiles(session, args.folder)
        else:
            print('Must supply a folder to scan')

    session.close()


if __name__ == '__main__':  # pragma: no cover
    main()
