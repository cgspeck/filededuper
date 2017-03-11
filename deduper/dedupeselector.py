# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import locale
import os
import pprint
import tkinter
import sys

from . import dialogs
from .util import Util


def Dedupe(session, suggest_mode=None, runmode='graphical', link=True, **kwargs):
    if runmode == 'graphical':
        tk_root = tkinter.Tk()
        tk_root.withdraw()
        dlg = dialogs.HeroImageWithList(tk_root)
    elif runmode == 'cli':
        locale.setlocale(locale.LC_ALL, '')
        dlg = dialogs.faux_tk_dialog("File deduper")
        # dialog.Dialog(dialog="dialog")

    dupes = Util.get_data(session, suggest_mode=suggest_mode)

    for dupe in dupes:
        assert 'keep_suggestions' in dupe, 'Dupe record must have a keep_suggestions field'
        assert len(dupe['keep_suggestions']), 'keep_suggestions must have at least one item in it'
        print('Will suggest keeping {record}'.format(
            record=dupe['keep_suggestions']))
        selected_keepers = []

        if runmode != 'auto':
            dialog_list = []

            for candidate_file in dupe['files']:
                suggest = True if (candidate_file['id'] in [r['id'] for r in dupe['keep_suggestions']]) else False

                dialog_list.append({
                    'name': candidate_file['name'],
                    'id': candidate_file['id'],
                    'fullpath': candidate_file['fullpath'],
                    'suggest': suggest})

            dlg.create_symlinks = link
            dlg.data = dialog_list
            dlg.mtitle = "Please select the file you would like to link to" if link else "Please select the files you would like to keep"
            dlg.window_init()

            if dlg.quit:
                print('Exiting')
                sys.exit()

            result = dlg.get_result()

            if not result:
                print('No image selected to keep or cancel pressed')
                continue

            selected_keepers = list(map(lambda i: dupe['files'][i], result))

        elif runmode == 'auto':
            selected_keepers = dupe['keep_suggestions']

        assert selected_keepers is not None
        assert len(selected_keepers) > 0

        for fname in selected_keepers:
            pprint.pprint('Will retain {0}'.format(fname['fullpath']))
            assert os.path.exists(fname['fullpath'])

        Util.handle_files(
            session,
            dupe['files'],
            selected_keepers,
            dupe['hash'],
            link=link
        )
