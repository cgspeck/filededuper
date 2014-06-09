import hashlib
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from .models import ImageFile
from .util import Util


def ScanFiles(session, FOLDER):
    u = Util()
    for root, dirs, files in os.walk(FOLDER):
        for count, filename in enumerate(files):
            fullpath = os.path.join(root, filename)

            if u.FileRecordExists(session, fullpath):
                print('{count} of {length}: Skipping {filename}'.format(
                    count=count, length=len(files), filename=filename))
            else:
                print('{count} of {length}: Processing {filename}'.format(
                    count=count, length=len(files), filename=filename))
                new_file = ImageFile(name=filename, fullpath=fullpath,
                    filehash=u.HashFile(fullpath), keep=False)
                session.add(new_file)
                session.commit()

    session.close()
