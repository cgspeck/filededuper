import pprint

from .util import Util


def PrintPopularityList(session, mode):
    results = Util.get_data(session)
    if mode == 'csv':
        for result in results:
            # print row by row COUNT, SUGGESTION_TO_KEEP
            print("{count}, {name}".format(count=result['count'],
                name=result['keep_suggestion']['name']))
    else:
            # pretty print the json objects
            pprint.pprint(results)
