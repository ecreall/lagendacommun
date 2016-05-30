# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi

from pyramid.threadlocal import get_current_request


_marker = object()


class Memojito(object):
    propname = '_memojito_'

    def memoize(self, func):

        def memogetter(*args, **kwargs):
            inst = args[0]
            cache = getattr(inst, self.propname, _marker)
            if cache is _marker:
                setattr(inst, self.propname, dict())
                cache = getattr(inst, self.propname)

            # XXX this could be potentially big, a custom key should
            # be used if the arguments are expected to be big

            request_id = getattr(get_current_request(), 'request_id', None)
            if request_id:
                kwargs['request_id'] = request_id

            key = (func.__module__, func.__name__, args, tuple(sorted(kwargs.items())))
            val = cache.get(key, _marker)
            if val is _marker:
                val = func(*args, **kwargs)
                cache[key] = val
                setattr(inst, self.propname, cache)
            return val
        return memogetter


_m = Memojito()
memoize = _m.memoize


class RequestMemojito(object):
    propname = '_memojito_'

    def request_memoize(self, func):

        def memogetter(*args, **kwargs):
            request = get_current_request()
            cache = getattr(request, self.propname, _marker)
            if cache is _marker:
                setattr(request, self.propname, dict())
                cache = getattr(request, self.propname)

            # XXX this could be potentially big, a custom key should
            # be used if the arguments are expected to be big
            key = (func.__module__, func.__name__, args, tuple(sorted(kwargs.items())))
            val = cache.get(key, _marker)
            if val is _marker:
                val = func(*args, **kwargs)
                cache[key] = val
                setattr(request, self.propname, cache)
            return val
        return memogetter

_m = RequestMemojito()
request_memoize = _m.request_memoize
