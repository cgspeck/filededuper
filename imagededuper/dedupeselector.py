# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import locale
import os
import pprint
import tkinter

import dialog

from . import dialogs
from .util import Util


def Dedupe(session, suggest_mode=None, runmode='graphical'):
    if runmode == 'graphical':
        tk_root = tkinter.Tk()
        tk_root.withdraw()
        dlg = dialogs.HeroImageWithList(tk_root)
    elif runmode == 'cli':
        locale.setlocale(locale.LC_ALL, '')
        dlg = dialog.Dialog(dialog="dialog")
        dlg.set_background_title("File deduper")

    dupes = Util.get_data(session, suggest_mode=suggest_mode)

    for dupe in dupes:
        assert 'keep_suggestion' in dupe
        print('Will suggest keeping {record}'.format(
            record=dupe['keep_suggestion']))
        selected_keeper = None

        if runmode == 'graphical':
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
            selected_keeper = dupe['files'][result[0]]
        elif runmode == 'cli':
            dialog_list = [('{0}'.format(count), name) for count, name in
                enumerate([candidate_file['name'] for candidate_file in
                    dupe['files']])]
            dialog_list.insert(0, ('-1', dupe['keep_suggestion']['name']))

            rc, selected = dlg.menu(text='Select a file to keep',
                choices=dialog_list)

            if rc == 'ok':
                if selected == '-1':
                    selected_keeper = dupe['keep_suggestion']
                else:
                    selected_keeper = dupe['files'][int(selected)]
            else:
                print('No image selected to keep or cancel pressed')
                break

        elif runmode == 'auto':
            selected_keeper = dupe['keep_suggestion']

        assert selected_keeper is not None
        assert os.path.exists(selected_keeper['fullpath'])
        pprint.pprint('Will retain {0}'.format(selected_keeper))

        Util.handle_files(session, dupe['files'], selected_keeper,
            dupe['hash'])
