from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class ImageFile(Base):
    __tablename__ = 'imagefiles'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullpath = Column(String)
    filehash = Column(String)
    keep = Column(Boolean)

    def __repr__(self):
        rs = "<ImageFile(name='%s', fullpath='%s', filehash='%s', keep='%s')>"
        return rs % (self.name, self.fullpath, self.filehash, self.keep)
