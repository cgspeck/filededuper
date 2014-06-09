import builtins

import fudge
import pytest

from imagededuper.util import Util
from imagededuper.models import ImageFile


@fudge.test
def test_hash_file(monkeypatch):

    fake_buffer = b'test'

    fake_empty_buffer = b''

    fake_filehandle = (fudge.Fake('file').provides('read')
        .with_args(65536).returns(fake_buffer)
        .next_call()
        .with_args(65536).returns(fake_empty_buffer)
        .provides('close'))

    fake_open = (fudge.Fake('open').expects_call()
        .with_args('/a/folder/0.ext', 'rb')
        .returns(fake_filehandle))

    monkeypatch.setattr(builtins, "open", fake_open)

    assert "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" \
        == Util.hash_file('/a/folder/0.ext')


def test_get_data(db_session):
    # returns a json dict of files with matching hashes in groups
    unique_file_1 = ImageFile(name='0.ext', fullpath='/a/folder/0.ext',
                    filehash='hash0')
    unique_file_2 = ImageFile(name='1.ext', fullpath='/a/folder/1.ext',
                    filehash='hash1')
    common_file_1a = ImageFile(name='cf1a.ext', fullpath='/a/folder/cf1a.ext',
                    filehash='cf1')
    common_file_1b = ImageFile(name='cf1b.ext', fullpath='/a/folder/cf1b.ext',
                    filehash='cf1')
    common_file_1c = ImageFile(name='cf1c.ext', fullpath='/a/folder/cf1cx.ext',
                    filehash='cf1')
    common_file_2a = ImageFile(name='cf2a.ext', fullpath='/a/folder/cf2a.ext',
                    filehash='cf2')
    common_file_2b = ImageFile(name='cf2b.ext', fullpath='/a/folder/cf2b.ext',
                    filehash='cf2')
    common_file_2c = ImageFile(name='cf2c.ext', fullpath='/a/folder/cf2cx.ext',
                    filehash='cf2')
    db_session.add(unique_file_1)
    db_session.add(unique_file_2)
    db_session.add(common_file_1a)
    db_session.add(common_file_1b)
    db_session.add(common_file_1c)
    db_session.add(common_file_2a)
    db_session.add(common_file_2b)
    db_session.add(common_file_2c)    
    db_session.commit()
    print(Util.get_data(db_session))