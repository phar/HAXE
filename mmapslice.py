import os

class MmapSlice(object):
    """create a proxy object for a mmap that views
    only part of the mmap buffer, given by offset and length.
    >>> import mmap
    >>> buf = mmap.mmap(-1,10)
    >>> buf[:6] = "foobar"
    >>> s = MmapSlice(buf, 3)
    >>> s[:3]
    'bar'
    >>> s[3:7] = "!!!!"
    >>> str(buf[:])
    'foobar!!!!'
    """
    def __init__(self, buf, offset=0, length=None):
        self.buf = buf
        self.offset = offset
        if length is None or length > len(buf)-offset:
            self.length = len(buf) - offset
        else:
            self.length = length
        self.stop = offset + self.length
        self._pos = 0

    def _checkstart(self, index):
        if index >= 0 and index < self.stop:
            return
        raise IndexError("index out of range: {}. valid range is [{} ,  {})".format(index, 0, self.stop))

    def _checkstop(self, index):
        if index >= 0 and index <= self.stop:
            return
        raise IndexError("stop index out of range: {}. valid range is [{} ,  {}]".format(index, 0, self.stop))


    def _i2i(self, index):
        if isinstance(index, slice):
            if index.start is None:
                start = self.offset
            else:
                start = index.start + self.offset
            if index.stop is None:
                stop = self.stop
            elif index.stop < 0:
                stop = index.stop + self.stop
            else:
                stop = index.stop + self.offset
            self._checkstop(stop)
            step = index.step
        elif isinstance(index, int):
            start = index + self.offset
            stop = start+1
            step = None
        else:
            raise IndexError("index out of range")
        self._checkstart(start)
        return slice(start,stop,step)


    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._checkstart(value)
        self._pos = value


    def read(self, num_bytes=1):
        pos = self.pos
        self.pos += num_bytes
        return self[pos]

    def seek(self, pos, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self.pos = pos
        elif whence == os.SEEK_CUR:
            self.pos += pos
        elif whence == os.SEEK_END:
            self.pos = self.stop + pos

    def tell(self):
        return self.pos

    def __getitem__(self, index):
        return self.buf[self._i2i(index)]

    def __setitem__(self, index, value):
        self.buf[self._i2i(index)] = value

    def __len__(self):
        return self.length

    def size(self):
        return len(self)

    def find(self, string, start=0, end=None):
        s = self._i2i(slice(start,end))
        i = self.buf.find(string, s.start, s.stop)
        return i - self.offset

    def rfind(self, string, start=0, end=None):
        s = self._i2i(slice(start,end))
        i = self.buf.rfind(string, s.start, s.stop)
        return i - self.offset

    def move(self, dest, src, count):
        dest += self.offset
        src += self.offset
        return self.buf.move(dest, src, count)

if __name__ == '__main__':
    buf = "asfd"
    s = MmapSlice(buf, 2)
    print (s[:])
