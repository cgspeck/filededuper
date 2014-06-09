import os
import py.test
import pytest
import functools
#from os import walk
import sys
import fudge
#from fudge import patch as fudge_patch, Fake
#from mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models
from imagededuper import scanfiles

import ipdb # import set_trace
from ipdb import set_trace

import fudge

#from fudge import patch as fudge_patch
#import functools

@pytest.fixture(scope='function')
def blank_db(request):
    engine = create_engine('sqlite:///:memory:', echo=True)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)
    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session

#@fudge.patch('scanfiles.HashFile')
#@fudge.patch('os.walk', 'scanfiles.HashFile')
#def test_scanner('fake:os.walk'):
#@patch('os.walk')
#@fudge.patch('os.walk')
#@patch('os.walk')
def test_scanner(blank_db, monkeypatch):

    #fake_walk = fudge.patch('os.walk')
    fake_walk = (fudge.Fake('walk').expects_call()
        .with_args('/a/folder')
        .returns([('/a/folder', [],
        ['/a/folder/{0}.ext'.format(num) for num in range(3)])]))
    
    monkeypatch.setattr(os, "walk", fake_walk)

    fake_HashFile = (fudge.Fake('HashFile')
        .is_callable()
        .with_args('/a/folder/0.ext').returns('HASH0')
        .with_args('/a/folder/1.ext').returns('HASH1')
        .with_args('/a/folder/2.ext').returns('HASH2')
        )

    monkeypatch.setattr(scanfiles, "HashFile", fake_HashFile)
    scanfiles.ScanFiles(blank_db, '/a/folder')
    fudge.verify()
    
