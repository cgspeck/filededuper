import hashlib

from .models import ImageFile


class Util(object):
    def file_record_exists(self, session, fullpath):
        query = session.query(ImageFile).filter(
            ImageFile.fullpath.like(fullpath))
        return not (query.first() is None)

    def hash_file(self, fullpath, blocksize=65536):
        print('!' * 20)
        hasher = hashlib.sha256()
        afile = open(fullpath, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()
