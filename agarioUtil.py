__author__ = 'Robin'

# glue code
class event(object):
    def __init__(self, func):
        self.__doc__ = func.__doc__
        self._key = ' ' + func.__name__
    def __get__(self, obj, cls):
        try:
            return obj.__dict__[self._key]
        except KeyError, exc:
            be = obj.__dict__[self._key] = boundevent()
            return be

class boundevent(object):
    def __init__(self):
        self._fns = []
    def __iadd__(self, fn):
        self._fns.append(fn)
        return self
    def __isub__(self, fn):
        self._fns.remove(fn)
        return self
    def __call__(self, *args, **kwargs):
        for f in self._fns[:]:
            f(*args, **kwargs)