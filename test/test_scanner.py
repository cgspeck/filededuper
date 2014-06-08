import py.test
import pytest
import functools
from os import walk
import sys
import fudge
from fudge import patch as fudge_patch, Fake

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models

import ipdb # import set_trace
from ipdb import set_trace


def wraps(func):
    def inner(f):
        f = functools.wraps(func)(f)
        original = getattr(func, '__wrapped__', func)
        f.__wrapped__ = original
        return f
    return inner


class patch(fudge_patch):
    pass

    def __call__(self, fn):

        @wraps(fn)
        def caller(*args, **kw):
            fakes = self.__enter__()
            if not isinstance(fakes, (tuple, list)):
                fakes = [fakes]
            args += tuple(fakes)
            value = None
            try:
                value = fn(*args, **kw)
            except:
                etype, val, tb = sys.exc_info()
                self.__exit__(etype, val, tb)
                #raise etype, val, tb
                sys.exit()
            else:
                self.__exit__(None, None, None)
            return value

        # py.test uses the length of mock.patchings to determine how many
        # arguments to ignore when performing its dependency injection
        if not hasattr(caller, 'patchings'):
            caller.patchings = []
        caller.patchings.extend([1 for path in self.obj_paths])
        return caller


@pytest.fixture(scope='function')
def blank_db(request):
    engine = create_engine('sqlite:///:memory:', echo=True)
    session = sessionmaker(bind=engine)
    models.Base.metadata.create_all(engine)
    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session




#@fudge.patch('scanfiles.HashFile')
#@fudge.patch('os.walk', 'scanfiles.HashFile')
#def test_scanner('fake:os.walk'):
#@patch('os.walk')
@fudge.patch('os.walk')
def test_scanner(blank_db, fake:os.walk):

    #fake_walk = fudge.patch('os.walk')
    (walk.expects_call()
        .with_args('/a/folder')
        .returns([('/a/folder', [],
        ['/a/folder/{0}.ext'.format(num) for num in range(3)])])
        )

    fake_HashFile = fudge.patch('scanfiles.HashFile')
    (fake_HashFile.remember_order()
        .expects('/a/folder/0.ext').returns('HASH0')
        .expects('/a/folder/1.ext').returns('HASH1')
        .expects('/a/folder/2.ext').returns('HASH2')
        )
    scanfiles.ScanFiles('/a/folder')
    fudge.verify()
    
