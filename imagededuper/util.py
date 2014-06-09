import hashlib

from .models import ImageFile


class Util(object):
    @staticmethod
    def file_record_exists(session, fullpath):
        query = session.query(ImageFile).filter(
            ImageFile.fullpath.like(fullpath))
        return not (query.first() is None)

    @staticmethod
    def hash_file(fullpath, blocksize=65536):
        print('!' * 20)
        hasher = hashlib.sha256()
        afile = open(fullpath, 'rb')
        buf = afile.read(blocksize)
        #from ipdb import set_trace; set_trace()
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        return hasher.hexdigest()
