# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import fudge
import pytest

import tkinter
import os
import dialog

from deduper import dialogs
from deduper import dedupeselector
from deduper import util
from deduper.models import ImageFile


@fudge.test
def test_imagemodel_tojson(monkeypatch, db_session):
    id_ = 1
    name = 'somename'
    fullpath = 'some/full/path'
    filehash = 'some-file-hash'

    new_file = ImageFile(
        id=id_,
        name=name,
        fullpath=fullpath,
        filehash=filehash
    )
    db_session.add(new_file)
    db_session.commit()

    assert new_file.to_dict() == {
        'id': id_,
        'name': name,
        'fullpath': fullpath,
        'hash': filehash
    }
