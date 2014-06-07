import hashlib
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from .models import ImageFile

def FileRecordExists(session, fullpath):
    query = session.query(ImageFile).filter(ImageFile.fullpath.like(fullpath))
    return not (query.first() is None)


def HashFile(fullpath, blocksize=65536):
    hasher = hashlib.sha256()
    afile = open(fullpath, 'rb')
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def ScanFiles(session, FOLDER):
    for root, dirs, files in os.walk(FOLDER):
        for count, filename in enumerate(files):
            fullpath = os.path.join(root, filename)

            if FileRecordExists(session, fullpath):
                print('{count} of {length}: Skipping {filename}'.format(
                    count=count, length=len(files), filename=filename))
            else:
                print('{count} of {length}: Processing {filename}'.format(
                    count=count, length=len(files), filename=filename))
                new_file = ImageFile(name=filename, fullpath=fullpath,
                    filehash=HashFile(fullpath), keep=False)
                session.add(new_file)
                session.commit()

    session.close()
