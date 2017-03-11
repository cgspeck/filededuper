# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import pprint

from .util import Util


def PrintPopularityList(session, print_mode='csv', suggest_mode=None, **kwargs):
    results = Util.get_data(session)
    if print_mode == 'csv':
        for result in results:
            # print row by row COUNT, SUGGESTION_TO_KEEP
            print("{count}, {name}".format(count=result['count'],
                name=result['keep_suggestion']['name']))
    else:
            # pretty print the json objects
            pprint.pprint(results)
