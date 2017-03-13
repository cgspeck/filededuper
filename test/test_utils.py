# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import builtins

import fudge

from deduper.util import Util
from deduper.models import ImageFile


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
        "_098f6bcd4621d373cade4e832627b4f6"\
         == Util.hash_file('/a/folder/0.ext')


def test_get_data(db_session):
    # returns a json dict of files with matching hashes in groups
    unique_file_1 = ImageFile(id=1, name='0.ext', fullpath='/a/folder/0.ext', filehash='hash0')
    unique_file_2 = ImageFile(id=2, name='1.ext', fullpath='/a/folder/1.ext', filehash='hash1')
    common_file_1a = ImageFile(id=3, name='cf1a.ext', fullpath='/a/folder/cf1a.ext', filehash='cf1')
    common_file_1b = ImageFile(id=4, name='cf1b.ext', fullpath='/a/folder/cf1b.ext', filehash='cf1')
    common_file_1c = ImageFile(id=5, name='cf1cx.ext', fullpath='/a/folder/cf1cx.ext', filehash='cf1')
    common_file_2a = ImageFile(id=6, name='cf2a.ext', fullpath='/a/folder/cf2a.ext', filehash='cf2')
    common_file_2b = ImageFile(id=7, name='cf2bx.ext', fullpath='/a/folder/cf2bx.ext', filehash='cf2')
    common_file_2c = ImageFile(id=8, name='cf2c.ext', fullpath='/a/folder/cf2c.ext', filehash='cf2')
    db_session.add(unique_file_1)
    db_session.add(unique_file_2)
    db_session.add(common_file_1a)
    db_session.add(common_file_1b)
    db_session.add(common_file_1c)
    db_session.add(common_file_2a)
    db_session.add(common_file_2b)
    db_session.add(common_file_2c)
    db_session.commit()

    expected = [
        {
            'hash': 'cf1', 'count': 3, 'files': [
                common_file_1a.to_dict(),
                common_file_1b.to_dict(),
                common_file_1c.to_dict(),
            ],
            'keep_suggestions': [
                common_file_1c.to_dict(),
            ]
        },
        {
            'hash': 'cf2', 'count': 3, 'files': [
                common_file_2a.to_dict(),
                common_file_2b.to_dict(),
                common_file_2c.to_dict(),
            ],
            'keep_suggestions': [
                common_file_2b.to_dict(),
            ]
         }
    ]

    actual = Util.get_data(db_session)

    assert expected == actual


def test_get_data_shortest(db_session):
    # returns a json dict of files with matching hashes in groups
    common_file_1a = ImageFile(
        name='cf1.ext', fullpath='/a/folder/cf1.ext', filehash='cf1', id=1
    )
    common_file_1b = ImageFile(
        name='cf1b.ext', fullpath='/b/folder/cf1b.ext', filehash='cf1', id=2
    )
    common_file_1c = ImageFile(
        name='cf1cx.ext', fullpath='/c/folder/cf1cx.ext', filehash='cf1', id=3
    )
    common_file_2a = ImageFile(
        name='cf2.ext', fullpath='/a/folder/cf2.ext', filehash='cf2', id=4
    )
    common_file_2b = ImageFile(
        name='cf2b.ext', fullpath='/b/folder/cf2b.ext', filehash='cf2', id=5
    )
    common_file_2c = ImageFile(
        name='cf2c.ext', fullpath='/c/folder/cf2c.ext', filehash='cf2', id=6
    )
    db_session.add(common_file_1a)
    db_session.add(common_file_1b)
    db_session.add(common_file_1c)
    db_session.add(common_file_2a)
    db_session.add(common_file_2b)
    db_session.add(common_file_2c)
    db_session.commit()

    expected = [
        {
            'hash': 'cf1', 'count': 3, 'files': [
                common_file_1a.to_dict(),
                common_file_1b.to_dict(),
                common_file_1c.to_dict(),
            ],
            'keep_suggestions': [
                common_file_1a.to_dict(),
            ]
        },
        {
        'hash': 'cf2', 'count': 3, 'files': [
            common_file_2a.to_dict(),
            common_file_2b.to_dict(),
            common_file_2c.to_dict(),
        ],
        'keep_suggestions': [
            common_file_2a.to_dict(),
        ]
         }
    ]

    actual = Util.get_data(db_session, suggest_mode='shortest_name')

    assert expected == actual

def test_get_data_with_deletepath(db_session):
    ''' Test the select by delete path method.
        It should return a list to files to keep that are not within the specified directory
    '''
    common_file_1a = ImageFile(
        name='cf1.ext', fullpath='/a/folder/cf1.ext', filehash='cf1', id=1
    )
    common_file_1b = ImageFile(
        name='cf1b.ext', fullpath='/b/folder/cf1b.ext', filehash='cf1', id=2
    )
    common_file_1c = ImageFile(
        name='cf1cx.ext', fullpath='/c/folder/cf1cx.ext', filehash='cf1', id=3
    )
    common_file_2a = ImageFile(
        name='cf2a.ext', fullpath='/a/folder/cf2a.ext', filehash='cf2', id=4
    )
    common_file_2b = ImageFile(
        name='cf2b.ext', fullpath='/b/folder/cf2b.ext', filehash='cf2', id=5
    )
    common_file_2c = ImageFile(
        name='cf2c.ext', fullpath='/c/folder/cf2c.ext', filehash='cf2', id=6
    )
    db_session.add(common_file_1a)
    db_session.add(common_file_1b)
    db_session.add(common_file_1c)
    db_session.add(common_file_2a)
    db_session.add(common_file_2b)
    db_session.add(common_file_2c)
    db_session.commit()

    expected = [
        {'hash': 'cf1', 'count': 3, 'files': [
            common_file_1a.to_dict(),
            common_file_1b.to_dict(),
            common_file_1c.to_dict(),
        ],
        'keep_suggestions':
            [
                common_file_1a.to_dict(),
                common_file_1c.to_dict(),
            ]
         },
        {'hash': 'cf2', 'count': 3, 'files': [
            common_file_2a.to_dict(),
            common_file_2b.to_dict(),
            common_file_2c.to_dict(),
        ],
        'keep_suggestions':
            [
                common_file_2a.to_dict(),
                common_file_2c.to_dict(),
            ]
         }
    ]

    actual = Util.get_data(db_session, suggest_mode='delete_path', delete_path='/b')

    assert expected == actual
