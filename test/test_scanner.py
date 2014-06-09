import os
import pytest
import fudge

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models
from imagededuper.models import ImageFile
from imagededuper import scanfiles
from imagededuper.util import Util


@pytest.fixture(scope='function')
def db_session(request):
    engine = create_engine('sqlite:///:memory:', echo=True)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)

    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session


@fudge.test
def test_scanner_happy_path(db_session, monkeypatch):
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
    scanfiles.ScanFiles(db_session, '/a/folder')

    qry = db_session.query(ImageFile)

    assert qry.count() == 3

    for i in range(3):
        qry = db_session.query(ImageFile).filter(
            ImageFile.filehash == 'HASH{0}'.format(i),
            ImageFile.name == '{0}.ext'.format(i),
            ImageFile.fullpath == '/a/folder/{0}.ext'.format(i)
        )
        assert qry.count() == 1


@fudge.test
def test_scanner_does_not_readd_files(db_session, monkeypatch):
    new_file = ImageFile(name='0.ext', fullpath='/a/folder/0.ext',
                    filehash='hash0')
    db_session.add(new_file)
    db_session.commit()

    fake_walk = (fudge.Fake('walk').expects_call()
        .with_args('/a/folder')
        .returns([('/a/folder', [],
        ['{0}.ext'.format(num) for num in range(1)])]))

    monkeypatch.setattr(os, "walk", fake_walk)

    fake_hash_file = (fudge.Fake('hash_file'))
    monkeypatch.setattr(Util, "hash_file", fake_hash_file)

    scanfiles.ScanFiles(db_session, '/a/folder')

    qry = db_session.query(ImageFile)

    assert qry.count() == 1
