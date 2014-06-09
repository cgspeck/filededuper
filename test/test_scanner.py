import os
import py.test
import pytest
import functools
import sys
import fudge

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models
from imagededuper.models import ImageFile
from imagededuper import scanfiles
from imagededuper.util import Util

# import ipdb # import set_trace


import fudge

@pytest.fixture(scope='function')
def test_session(request):
    engine = create_engine('sqlite:///:memory:', echo=True)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)
    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session


def test_scanner(test_session, monkeypatch):

    fake_walk = (fudge.Fake('walk').expects_call()
        .with_args('/a/folder')
        .returns([('/a/folder', [],
        ['{0}.ext'.format(num) for num in range(3)])]))
    
    monkeypatch.setattr(os, "walk", fake_walk)

    fake_hash_file = (fudge.Fake('hash_file')
        .is_callable()
        .with_args('/a/folder/0.ext')
        .returns('HASH0')
        .next_call()
        .with_args('/a/folder/1.ext')
        .returns('HASH1')
        .next_call()
        .with_args('/a/folder/2.ext')
        .returns('HASH2')
        )

    monkeypatch.setattr(Util, "hash_file", fake_hash_file)
    scanfiles.ScanFiles(test_session, '/a/folder')

    qry = test_session.query(ImageFile)

    assert qry.count() == 3

    for i in range(3):
        qry = test_session.query(ImageFile).filter(
            ImageFile.filehash=='HASH{0}'.format(i)
            , ImageFile.name=='{0}.ext'.format(i)
            , ImageFile.fullpath=='/a/folder/{0}.ext'.format(i)
            )
        assert qry.count() == 1
