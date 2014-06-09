import os
import pprint

import tkinter

from ipdb import set_trace  # noqa

from .printpopularitylist import get_data
from .models import ImageFile
from .dialogs import HeroImageWithList


def GraphicalDedupe(session):
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    dlg = HeroImageWithList(tk_root)

    dupes = get_data(session)

    if len(dupes) == 0:
        print('No duplicate files detected')
        return

    for dupe in dupes:
        assert 'keep_suggestion' in dupe
        print('Will suggest keeping {record}'.format(
            record=dupe['keep_suggestion']))

        dialog_list = []

        for candidate_file in dupe['files']:
            suggest = True if (candidate_file['id'] ==
                dupe['keep_suggestion']['id']) else False

            dialog_list.append({
                'name': candidate_file['name'],
                'id': candidate_file['id'],
                'fullpath': candidate_file['fullpath'],
                'suggest': suggest})

        dlg.data = dialog_list
        dlg.mtitle = "Please select the file you would like to keep"
        dlg.window_init()
        if not dlg.result:
            print('No image selected to keep or cancel pressed')
            break

        selected_keeper = dupe['files'][dlg.result[0]]

        assert selected_keeper is not None
        assert os.path.exists(selected_keeper['fullpath'])

        pprint.pprint('Will retain {0}'.format(selected_keeper))

        for candidate_file in dupe['files']:
            if candidate_file['id'] != selected_keeper['id']:
                try:
                    print('Deleting {0}'.format(candidate_file['fullpath']))

                except Exception:
                    raise
                finally:
                    pass
            else:
                print('Keeping {name}'
                    .format(name=candidate_file['name']))

        session.query(ImageFile) \
            .filter(ImageFile.filehash == dupe['hash'],
                ImageFile.id != selected_keeper['id'])\
            .delete()
        session.commit()
