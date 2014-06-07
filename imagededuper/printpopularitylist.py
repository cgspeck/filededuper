import pprint

from sqlalchemy.sql import func
from ipdb import set_trace  # noqa

from .models import ImageFile


def get_data(session):
    results = []

    qry = session.query(ImageFile.filehash,
    func.count('*').label('hash_count'))\
    .group_by(ImageFile.filehash).having(func.count('*') > 1)

    for filehash, count in session.query(ImageFile.filehash, func.count('*')
            .label('hash_count')).group_by(ImageFile.filehash)\
            .having(func.count('*') > 1).order_by('hash_count desc'):
        qry = session.query(ImageFile.name,
            func.char_length(ImageFile.name).label('namelen'))\
            .filter(ImageFile.filehash == filehash)
        assert qry.count() == count
        max_len = 0
        result_to_keep = None

        files = []
        keep_suggestion = None

        for result in qry:
            files.append(result.name)
            if result.namelen > max_len:
                keep_suggestion = result.name
                max_len = result.namelen
        # make sure we have set a file to save
        assert keep_suggestion
        results.append(dict(hash=filehash, count=count, files=files,
            keep_suggestion=keep_suggestion))

    return results



def PrintPopularityList(session, mode):
    results = get_data(session)
    if mode == 'csv':
        for result in results:
            # print row by row COUNT, SUGGESTION_TO_KEEP
            print("{count}, {name}".format(count=result['count'],
                name=result['keep_suggestion']))
    else:
            # pretty print the json objects
            pprint.pprint(results)

