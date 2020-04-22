import os
from sqlalchemy.ext.declarative import declarative_base
from .models import ImageFile
from .util import Util

Base = declarative_base()


def ScanFiles(session, FOLDER):
    for root, dirs, files in os.walk(FOLDER):
        if root.split('/')[-1].startswith('.'):
            continue

        for count, filename in enumerate(files, start=1):
            if filename.startswith('.'):
                continue

            fullpath = os.path.join(root, filename)

            if not os.path.isfile(fullpath):
                continue

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
