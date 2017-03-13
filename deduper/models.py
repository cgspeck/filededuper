# This file is part of the File Deduper project. It is subject to
# the the revised 3-clause BSD license terms as set out in the LICENSE
# file found in the top-level directory of this distribution. No part of this
# project, including this file, may be copied, modified, propagated, or
# distributed except according to the terms contained in the LICENSE fileself.
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class ImageFile(Base):
    __tablename__ = 'imagefiles'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullpath = Column(String)
    filehash = Column(String)

    def __repr__(self):
        rs = "<ImageFile(name='%s', fullpath='%s', filehash='%s')>"
        return rs % (self.name, self.fullpath, self.filehash)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'fullpath': self.fullpath,
            'hash': self.filehash
        }


def create_tables(engine):
    Base.metadata.create_all(engine)
