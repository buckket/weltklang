from sqlalchemy.orm import relationship, mapper
from sqlalchemy import Table
from ConfigParser import SafeConfigParser
from itertools import count, izip
from collections import OrderedDict, Set
import os


CONFIG = SafeConfigParser()


class SET(Set):
    def __init__(self, iterable = ()):
        self.num = count()
        self.dict = OrderedDict(izip(iterable, self.num))
    def add(self, elem):
        if elem not in self:
            self.dict[elem] = next(self.num)
    def index(self, elem):
        return self.dict[elem]
    def __contains__(self, elem):
        return elem in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __repr__(self):
        return 'SET({})'.format(self.dict.keys())
    def __getattr__(self, name):
        if name in self:
            return 1 << (self.index(name))
        raise AttributeError
    def name(self,mask):
        for elem in self:
            if mask & 1 << self.index(elem):
                return elem


class ENUM(Set):
    def __init__(self, iterable = ()):
        self.num = count()
        self.dict = OrderedDict(izip(iterable, self.num))
    def add(self, elem):
        if elem not in self:
            self.dict[elem] = next(self.num)
    def index(self, elem):
        return self.dict[elem]
    def __contains__(self, elem):
        return elem in self.dict
    def __len__(self):
        return len(self.dict)
    def __iter__(self):
        return iter(self.dict)
    def __repr__(self):
        return 'ENUM({})'.format(self.dict.keys())
    def __getattr__(self, name):
        if name in self:
            return self.index(name)
        raise AttributeError


def init(basepath):
    CONFIG.read(os.path.join(basepath, 'etc', 'config.cfg'))
