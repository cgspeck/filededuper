import builtins
import os
import pytest
import fudge

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models
from imagededuper.models import ImageFile
from imagededuper import scanfiles
from imagededuper.util import Util


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

