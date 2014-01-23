from collections import deque
from itertools import count, izip
from collections import OrderedDict, Set


class RingBuffer(deque):
    """
    inherits deque, pops the oldest data to make room
    for the newest data when size is reached
    """

    def __init__(self, size):
        deque.__init__(self)
        self.size = size
        self.offset = 0

    def full_append(self, item):
        deque.append(self, item)
        # full, pop the oldest item, left most item
        self.popleft()
        self.offset += 1

    def append(self, item):
        deque.append(self, item)
        # max size reached, append becomes full_append
        if len(self) == self.size:
            self.append = self.full_append

    def get(self):
        """returns a list of size items (newest items)"""
        return list(self)


class SET(Set):
    def __init__(self, iterable=()):
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

    def name(self, mask):
        for elem in self:
            if mask & 1 << self.index(elem):
                return elem


class ENUM(Set):
    def __init__(self, iterable=()):
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

    def tuples(self):
        ret = []
        for name in self:
            ret.append((self.index(name), name))
        return ret

    def indexof(self, index):
        for name in self:
            if self.index(name) == index:
                return name
