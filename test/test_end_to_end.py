import pytest

import os
from tempfile import TemporaryDirectory

from deduper import  dedupeselector, scanfiles

class SampleFile(object):
    def __init__(self, root, path, name, contents=None):
        if contents is None:
            contents = name

        dir_path = os.path.join(root, path)
        os.makedirs(dir_path, exist_ok=True)
        self.fullpath = os.path.join(dir_path, name)
        with open(self.fullpath, 'wt') as f:
            f.write(contents)
        print('%s written' % self.fullpath)

    def exists(self):
        return os.path.exists(self.fullpath)

    def subdir(self):
        return self.fullpath.split('/')[-2]

    def fullpath(self):
        return self.fullpath

@pytest.fixture(scope='function')
def fileset(request):
    with TemporaryDirectory() as root:
        print('tempfiles are in %s' % root)
        res = {}
        res['root'] = root
        collections = {}
        for i in ['a', 'b', 'c']:
            collections[i] = []
            for p in ['short', 'longer', 'longest']:
                collections[i].append(SampleFile(root, p, i))
        res['collections'] = collections
        yield res


def test_auto_delete_remove_path(db_session, fileset):
    scanfiles.ScanFiles(db_session, fileset['root'])
    delete_path = os.path.join(fileset['root'], 'longer')
    dedupeselector.Dedupe(
        db_session,
        suggest_mode='delete_path',
        runmode='auto',
        link=False,
        delete_path=delete_path
    )

    for category, sf_list in fileset['collections'].items():
        for sf in sf_list:
            if sf.fullpath.startswith(delete_path):
                assert not sf.exists()
            else:
                assert sf.exists()
