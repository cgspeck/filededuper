import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

import signal
import sys

import tkinter
import dlg_herocheckboxlist

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
qry = session.query(ImageFile.filehash, func.count('*').label('hash_count'))\
    .group_by(ImageFile.filehash).having(func.count('*') > 1)
tk_root = tkinter.Tk()
tk_root.withdraw()
dlg = dlg_herocheckboxlist.HeroCheckboxList(tk_root)

for filehash, count in session.query(ImageFile.filehash, func.count('*')
                                     .label('hash_count'))\
                                     .group_by(ImageFile.filehash)\
                                     .having(func.count('*') > 1)\
                                     .order_by('hash_count desc'):
    print("{count}:{hash}".format(hash=filehash, count=count))
    qry = session.query(ImageFile, func.char_length(ImageFile.name)
                        .label('namelen'))\
                        .filter(ImageFile.filehash == filehash)
    assert qry.count() == count

    # suggest keeping the file with the longest name
    id_to_keep = None
    result_to_keep = None

    max_len = 0
    result_to_keep = None

    for result in qry:
        if result.namelen > max_len:
            result_to_keep = result
            max_len = result.namelen

    assert result_to_keep
    print('Will suggest keeping {record}'.format(record=result_to_keep))

    dialog_list = []

    for result in qry:
        suggest = True if (result[0].id == result_to_keep[0].id) else False
        dialog_list.append({
            'name': result[0].name,
            'id': result[0].id,
            'fullpath': result[0].fullpath,
            'suggest': suggest})

    dlg.data = dialog_list
    dlg.suggested = result_to_keep[0].id
    dlg.mtitle = "Please select the image you'd like to keep"
    dlg.window_init()
    if not dlg.result:
        print('No image selected to keep or cancel pressed')
        break

    selected_keeper = qry[dlg.result[0]]

    assert os.path.exists(result_to_keep[0].fullpath)
    assert result_to_keep in qry

    for record in qry:
        if record != result_to_keep:
            try:
                pass
            except Exception:
                raise
            finally:
                pass
        else:
            print('Selected to keep {name}'
                .format(name=selected_keeper[0].name))


session.close()
