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
            if result.namelen > max_len:
                keep_suggestion = result
                max_len = result.namelen
        # make sure we have set a file to save
        assert keep_suggestion
        keep_suggestion = dict(name=keep_suggestion.name,
            fullpath=keep_suggestion.fullpath, id=keep_suggestion.id)

        results.append(dict(hash=filehash, count=count, files=files,
            keep_suggestion=keep_suggestion))

    return results


def PrintPopularityList(session, mode):
    results = get_data(session)
    if mode == 'csv':
        for result in results:
            # print row by row COUNT, SUGGESTION_TO_KEEP
            print("{count}, {name}".format(count=result['count'],
                name=result['keep_suggestion']['name']))
    else:
            # pretty print the json objects
            pprint.pprint(results)
