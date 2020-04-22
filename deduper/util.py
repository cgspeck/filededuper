# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
from copy import copy
from pprint import pprint
import hashlib
import os

from sqlalchemy.sql import func
from sqlalchemy import text

from . import models


class Util(object):
    @staticmethod
    def file_record_exists(session, fullpath):
        query = session.query(models.ImageFile).filter(
            models.ImageFile.fullpath.like(fullpath))
        return not (query.first() is None)

    @staticmethod
    def hash_file(fullpath, blocksize=65536):
        hasher1 = hashlib.sha256()
        hasher2 = hashlib.md5()
        afile = open(fullpath, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher1.update(buf)
            hasher2.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return '{0}_{1}'.format(hasher1.hexdigest(), hasher2.hexdigest())

    @staticmethod
    def get_data(session, suggest_mode=None, delete_path=None):
        results = Util._load_records(session)
        if suggest_mode not in ['longest_name', 'shortest_name', 'delete_path']:
            raise ValueError('Must specify a suggestion mode')

        if suggest_mode == 'delete_path' and delete_path is None:
            raise 'Must provide a path containing files that you want removed'

        for result in results:
            keep_suggestions = []

            for file_ in result['files']:
                if suggest_mode == 'delete_path' and not file_['fullpath'].startswith(delete_path):
                    keep_suggestions.append(copy(file_))
                    continue

                if len(keep_suggestions) == 0:
                    keep_suggestions = [file_]
                    max_len = len(file_['name'])

                if suggest_mode == 'longest_name' and len(file_['name']) > max_len:
                    print('bass')
                    keep_suggestions = [file_]
                    max_len = len(file_['name'])
                elif suggest_mode == 'shortest_name' and len(file_['name']) < max_len:
                    print('found a shorter path')
                    keep_suggestions = [file_]
                    max_len = len(file_['name'])

            # make sure we have set at least one file to save
            assert len(keep_suggestions) > 0
            result['keep_suggestions'] = keep_suggestions

        return results

    @staticmethod
    def _load_records(session):
        results = []

        qry = session.query(models.ImageFile.filehash,
            func.count('*').label('hash_count'))\
            .group_by(models.ImageFile.filehash).having(func.count('*') > 1)

        for filehash, count in session.query(models.ImageFile.filehash,
                func.count('*').label('hash_count'))\
                .group_by(models.ImageFile.filehash).having(func.count('*')
                    > 1).order_by(text('hash_count desc')):
            qry = session.query(models.ImageFile.id, models.ImageFile.name,
                models.ImageFile.fullpath, models.ImageFile.filehash,
                func.char_length(models.ImageFile.name).label('namelen'))\
                .filter(models.ImageFile.filehash == filehash)
            assert qry.count() == count

            files = []

            for result in qry:
                files.append(dict(name=result.name, fullpath=result.fullpath,
                    id=result.id, hash=result.filehash))
            results.append(dict(hash=filehash, count=count, files=files))

        return results

    @staticmethod
    def handle_files(session, candidates, selected_keepers, hash_, link=True):
        selected_ids = [s['id'] for s in selected_keepers]

        for candidate_file in candidates:
            if candidate_file['id'] not in selected_ids:
                try:
                    print('Deleting {0}'.format(candidate_file['fullpath']))
                    os.remove(candidate_file['fullpath'])
                except Exception:
                    print('Error deleting file!!')
                    session.close()
                    raise

                if link:
                    try:
                        print('Linking {0} to {1}'.format(
                            selected_keepers[0]['fullpath'],
                            candidate_file['fullpath']))
                        os.link(selected_keepers[0]['fullpath'],
                            candidate_file['fullpath'])
                    except Exception:
                        print('Error linking file!!')
                        session.close()
                        raise

            else:
                print('Keeping {name}'
                    .format(name=candidate_file['name']))

        session.query(models.ImageFile) \
            .filter(
                models.ImageFile.filehash == hash_,
                models.ImageFile.id.notin_(selected_ids)
            ) \
            .delete(synchronize_session='fetch')

        session.commit()
