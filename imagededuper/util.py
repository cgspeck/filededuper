import hashlib

from sqlalchemy.sql import func

from .models import ImageFile


class Util(object):
    @staticmethod
    def file_record_exists(session, fullpath):
        query = session.query(ImageFile).filter(
            ImageFile.fullpath.like(fullpath))
        return not (query.first() is None)

    @staticmethod
    def hash_file(fullpath, blocksize=65536):
        hasher = hashlib.sha256()
        afile = open(fullpath, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()

    @staticmethod
    def get_data(session, suggest_mode=None):
        if suggest_mode not in ['longest_name', 'shortest_name']:
            suggest_mode = 'longest_name'

        results = []

        qry = session.query(ImageFile.filehash,
            func.count('*').label('hash_count'))\
            .group_by(ImageFile.filehash).having(func.count('*') > 1)

        for filehash, count in session.query(ImageFile.filehash,
                func.count('*').label('hash_count'))\
                .group_by(ImageFile.filehash).having(func.count('*') > 1)\
                .order_by('hash_count desc'):
            qry = session.query(ImageFile.id, ImageFile.name,
                ImageFile.fullpath,
                func.char_length(ImageFile.name).label('namelen'))\
                .filter(ImageFile.filehash == filehash)
            assert qry.count() == count
            max_len = 0

            files = []
            keep_suggestion = None

            for result in qry:
                files.append(dict(name=result.name, fullpath=result.fullpath,
                    id=result.id))

                if keep_suggestion is None:
                    keep_suggestion = result
                    max_len = result.namelen

                if suggest_mode == 'longest_name':
                    if result.namelen > max_len:
                        keep_suggestion = result
                        max_len = result.namelen
                elif suggest_mode == 'shortest_name':
                    if result.namelen < max_len:
                        keep_suggestion = result
                        max_len = result.namelen

            # make sure we have set a file to save
            assert keep_suggestion
            keep_suggestion = dict(name=keep_suggestion.name,
                fullpath=keep_suggestion.fullpath, id=keep_suggestion.id)

            results.append(dict(hash=filehash, count=count, files=files,
                keep_suggestion=keep_suggestion))

        return results
