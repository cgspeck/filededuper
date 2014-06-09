import os
import py.test
import pytest
import functools
import sys
import fudge

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models
from imagededuper import scanfiles
from imagededuper.util import Util

import ipdb # import set_trace
from ipdb import set_trace

import fudge

@pytest.fixture(scope='function')
def blank_db(request):
    engine = create_engine('sqlite:///:memory:', echo=False)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)
    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session


def test_scanner(blank_db, monkeypatch):

    fake_walk = (fudge.Fake('walk').expects_call()
        .with_args('/a/folder')
        .returns([('/a/folder', [],
        ['/a/folder/{0}.ext'.format(num) for num in range(3)])]))
    
    monkeypatch.setattr(os, "walk", fake_walk)

    fake_hashfile = (fudge.Fake('HashFile')
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

    monkeypatch.setattr(Util, "HashFile", fake_hashfile)
    scanfiles.ScanFiles(blank_db, '/a/folder')
    
