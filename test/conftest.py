import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from imagededuper import models


@pytest.fixture(scope='function')
def db_session(request):
    engine = create_engine('sqlite:///:memory:', echo=False)
    session = sessionmaker(bind=engine)()
    models.Base.metadata.create_all(engine)

    def fin():
        models.Base.metadata.drop_all(engine)
    request.addfinalizer(fin)
    return session
