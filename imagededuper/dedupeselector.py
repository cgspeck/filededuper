import os
import pprint

import tkinter

from .models import ImageFile
from . import dialogs
from . import util


def GraphicalDedupe(session):
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    dlg = dialogs.HeroImageWithList(tk_root)

    dupes = util.Util.get_data(session)

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

        result = dlg.get_result()
        if not result:
            print('No image selected to keep or cancel pressed')
            break

        print(result)

        selected_keeper = dupe['files'][result[0]]
        assert selected_keeper is not None
        assert os.path.exists(selected_keeper['fullpath'])
        pprint.pprint('Will retain {0}'.format(selected_keeper))

        for candidate_file in dupe['files']:
            if candidate_file['id'] != selected_keeper['id']:
                try:
                    print('Deleting {0}'.format(candidate_file['fullpath']))
                    os.remove(candidate_file['fullpath'])
                except Exception:
                    print('Unable to delete file!!')
                    session.close()
                    raise
            else:
                print('Keeping {name}'
                    .format(name=candidate_file['name']))

        session.query(ImageFile) \
            .filter(ImageFile.filehash == dupe['hash'],
                ImageFile.id != selected_keeper['id'])\
            .delete()
        session.commit()
