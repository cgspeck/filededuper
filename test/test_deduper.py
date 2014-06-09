import fudge

import tkinter
import os

from imagededuper import dialogs
from imagededuper import dedupeselector
from imagededuper import util
from imagededuper.models import ImageFile


@fudge.test
def test_deduper(monkeypatch, db_session):
    fake_tk_root = fudge.Fake().provides('withdraw')
    fake_Tk = fudge.Fake('Tk').is_callable().returns(fake_tk_root)

    first_selection = (0, )  # select first file
    second_selection = (1, )  # select second file

    fake_dlg_instance = (fudge.Fake('HeroImageWithListInstance')
        .provides('window_init')
        .remember_order()
        .expects('get_result').returns(first_selection)
        .expects('get_result').returns(second_selection)
    )

    fake_HeroImageWithList = (fudge.Fake('HeroImageWithList').is_callable()
        .with_args(fake_tk_root)
        .returns(fake_dlg_instance)
    )

    fake_getdata_response = [
        {'hash': 'cf1', 'count': 3, 'files': [
            {'name': 'cf1a.ext', 'fullpath': '/a/folder/cf1a.ext', 'id': 3},
            {'name': 'cf1b.ext', 'fullpath': '/a/folder/cf1b.ext', 'id': 4},
            {'name': 'cf1cx.ext', 'fullpath': '/a/folder/cf1cx.ext', 'id': 5}],
        'keep_suggestion':
            {'name': 'cf1cx.ext', 'fullpath': '/a/folder/cf1cx.ext', 'id': 5}
         },
        {'hash': 'cf2', 'count': 3, 'files': [
            {'name': 'cf2a.ext', 'fullpath': '/a/folder/cf2a.ext', 'id': 6},
            {'name': 'cf2bx.ext', 'fullpath': '/a/folder/cf2bx.ext', 'id': 7},
            {'name': 'cf2c.ext', 'fullpath': '/a/folder/cf2c.ext', 'id': 8}],
        'keep_suggestion':
            {'name': 'cf2bx.ext', 'fullpath': '/a/folder/cf2bx.ext', 'id': 7}
         }
    ]

    # 1
    new_file = ImageFile(name='uniquefile', fullpath='/a/folder/cf1a.ext',
                    filehash='uf1')
    db_session.add(new_file)
    db_session.commit()
    # 2
    new_file = ImageFile(name='uniquefile2', fullpath='/a/folder/cf1a.ext',
                    filehash='uf2')
    db_session.add(new_file)
    db_session.commit()
    # 3
    new_file = ImageFile(name='thefileiwant', fullpath='/a/folder/cf1a.ext',
                    filehash='cf1')
    db_session.add(new_file)
    db_session.commit()
    # 4
    new_file = ImageFile(name='notthefileiwant', fullpath='/a/folder/cf1a.ext',
                    filehash='cf1')
    db_session.add(new_file)
    db_session.commit()
    # 5
    new_file = ImageFile(name='alsonotthefileiwant', fullpath='test',
                    filehash='cf1')
    db_session.add(new_file)
    db_session.commit()
    # 6
    new_file = ImageFile(name='thefileiwant', fullpath='test',
                    filehash='cf1')
    db_session.add(new_file)
    db_session.commit()
    # 7
    new_file = ImageFile(name='thefileiwant2', fullpath='test',
                    filehash='cf2')
    db_session.add(new_file)
    db_session.commit()
    # 8
    new_file = ImageFile(name='notthefileiwant2', fullpath='test',
                    filehash='cf2')
    db_session.add(new_file)
    db_session.commit()
    # 9
    new_file = ImageFile(name='alsonotthefileiwant2', fullpath='test',
                    filehash='cf2')
    db_session.add(new_file)
    db_session.commit()

    fake_exists = (fudge.Fake('exists').is_callable()
                    .with_args('/a/folder/cf1a.ext').returns(True)
                    .next_call()
                    .with_args('/a/folder/cf2bx.ext').returns(True)
                   )

    fake_remove = (fudge.Fake('remove').is_callable()
                    .with_args('/a/folder/cf1b.ext')
                    .next_call()
                    .with_args('/a/folder/cf1cx.ext')
                    .next_call()
                    .with_args('/a/folder/cf2a.ext')
                    .next_call()
                    .with_args('/a/folder/cf2c.ext')
                   )

    monkeypatch.setattr(dialogs, 'HeroImageWithList', fake_HeroImageWithList)
    monkeypatch.setattr(tkinter, 'Tk', fake_Tk)
    monkeypatch.setattr(os.path, 'exists', fake_exists)
    monkeypatch.setattr(os, 'remove', fake_remove)

    def fake_get_data(session):
        return fake_getdata_response

    monkeypatch.setattr(util.Util, 'get_data', fake_get_data)

    dedupeselector.GraphicalDedupe(db_session)

    # now check db
    assert [name_[0] for name_ in db_session.query(ImageFile.name)] ==\
        ['uniquefile', 'uniquefile2', 'thefileiwant', 'thefileiwant2']
    assert db_session.query(ImageFile).count() == 4
