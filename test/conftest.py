# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from deduper import models


@pytest.fixture(scope='function')
def db_session(request):
    engine = create_engine('sqlite:///:memory:', echo=False)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)

    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session
