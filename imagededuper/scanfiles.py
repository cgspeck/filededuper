# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import os

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .models import ImageFile
from .util import Util


def ScanFiles(session, FOLDER):
    for root, dirs, files in os.walk(FOLDER):
        for count, filename in enumerate(files):
            fullpath = os.path.join(root, filename)

            if Util.file_record_exists(session, fullpath):
                print('{count} of {length}: Skipping {filename}'.format(
                    count=count, length=len(files), filename=filename))
            else:
                print('{count} of {length}: Processing {filename}'.format(
                    count=count, length=len(files), filename=filename))
                new_file = ImageFile(name=filename, fullpath=fullpath,
                    filehash=Util.hash_file(fullpath))
                session.add(new_file)
                session.commit()

    session.close()
