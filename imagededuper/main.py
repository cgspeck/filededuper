#!/usr/bin/env python
import argparse
import functools
import datetime
import time
import signal
import logging
import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import scanfiles

def connect_to_db():
    engine = create_engine('sqlite:///images.sqlite3', echo=False)
    Session = sessionmaker(bind=engine)
    return Session()

def setup_logging():    # pragma: no cover
    log_format = '%(asctime)s:%(levelname)s:%(filename)s(%(lineno)d) ' \
        '%(message)s'
    log_level = logging.DEBUG
    logging.basicConfig(format=log_format, level=log_level)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    insp = frame
    while True:
        if 'session' in insp.f_locals:
            print('Closing database')
            insp.f_locals['session'].close()
            sys.exit()
        else:
            insp = frame.f_back
    sys.exit(0)

def silly_function():
    while True:
        print(datetime.datetime.now())
        time.sleep(1)

def main():  # pragma: no cover
    setup_logging()
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='Image file deduper')
    function_group = parser.add_mutually_exclusive_group()
    function_group.add_argument(
        '--scan', '-s', action='store_true',
        help='Scan given folder for image files and store hash')
    function_group.add_argument(
        '--printlist', '-p', action='store_true',
        help='Print duplicate hashes, count and file list')
    function_group.add_argument(
        '--dedupe', '-d', action='store_true',
        help='Interactively prompt to delete duplicate files')
    parser.add_argument('-db', '--db', default='sqlite:////~/dupeimages.db',
        help='Database URI, e.g. sqlite:////home/user/images.db')
    parser.add_argument('folder',  nargs='?', default=os.getcwd(),
        help='Folder to scan')

    parser.set_defaults(scan=True)
    args = parser.parse_args()

    session = connect_to_db()

    if args.printlist:
        pass
    elif args.dedupe:
        pass
    elif args.scan:
        if not args.folder:
            print('Must supply a folder to scan')
            sys.exit()

        scanfiles.ScanFiles(args.folder, session)        


if __name__ == '__main__':  # pragma: no cover
    main()