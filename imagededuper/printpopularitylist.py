from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import signal
import sys


from ipdb import set_trace  # noqa
engine = create_engine('sqlite:///images.sqlite3', echo=False)

from models import ImageFile

Session = sessionmaker(bind=engine)
session = Session()


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    session.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
qry = session.query(ImageFile.filehash,
    func.count('*').label('hash_count'))\
    .group_by(ImageFile.filehash).having(func.count('*') > 1)

for filehash, count in session.query(ImageFile.filehash, func.count('*')
        .label('hash_count')).group_by(ImageFile.filehash)\
        .having(func.count('*') > 1).order_by('hash_count desc'):
    qry = session.query(ImageFile,
        func.char_length(ImageFile.name).label('namelen'))\
        .filter(ImageFile.filehash == filehash)
    assert qry.count() == count
    max_len = 0
    result_to_keep = None

    for result in qry:
        if result.namelen > max_len:
            result_to_keep = result
            max_len = result.namelen

    print("{count}:{name}".format(count=count, name=result_to_keep[0].name))

session.close()
