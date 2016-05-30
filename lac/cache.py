# Copyright (c) 2016 by Ecreall under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html

# licence: AGPL
# author: Amen Souissi, Vincent Fretin

import inspect
from dogpile.cache import make_region, compat
#from dogpile.cache.util import sha1_mangle_key
from persistent import Persistent
from substanced.util import get_oid


def kw_function_key_generator(namespace, fn, to_str=compat.string_type):
    """Return a function that generates a string
    key, based on a given function as well as
    arguments to the returned function itself.

    This is used by :meth:`.CacheRegion.cache_on_arguments`
    to generate a cache key from a decorated function.

    It can be replaced using the ``function_key_generator``
    argument passed to :func:`.make_region`.

    """

    if namespace is None:
        namespace = '%s:%s' % (fn.__module__, fn.__name__)
    else:
        namespace = '%s:%s|%s' % (fn.__module__, fn.__name__, namespace)

    args = inspect.getargspec(fn)
    has_self = args[0] and args[0][0] in ('self', 'cls')
    def generate_key(*args, **kw):
        #if has_self:
        if has_self and args and isinstance(args[0], Persistent):
            # When the kw_function_key_generator is called via
            # the method, we get:
            # args = (<EDBAuthPlugin at /extranetPRIVR/acl_users/eap>, 'vincentfretin')
            # When called via method.invalidate we get:
            # args = ('vincentfretin',)
            args = args[1:]

        genkey = namespace + "|" + " ".join(
            [isinstance(arg, Persistent) and str(get_oid(arg, 'nooid')) or to_str(arg)
             for arg in args]
        )
        if kw:
            local_index = []
            for key, val in kw.items():
                local_index.append((to_str(key), to_str(val)))

            local_index.sort()
            for key, val in local_index:
                genkey += " %s:%s" % (key, val)

        return genkey
    return generate_key


#region_memcached = make_region(
#        function_key_generator=kw_function_key_generator,
#        key_mangler=sha1_mangle_key
#).configure(
#'dogpile.cache.memcached',
#expiration_time=3600,
#arguments={
#    'url': ["127.0.0.1:11211"],
#    'min_compress_len': 1000,
#    'distributed_lock': True,
#},
#)

region_memory = make_region(function_key_generator=kw_function_key_generator
    ).configure(
#    "dogpile.cache.memory_pickle",
    "dogpile.cache.memory",
    expiration_time=3600,
    )

region_null = make_region(function_key_generator=kw_function_key_generator
    ).configure(
    "dogpile.cache.null")

#region = region_memcached
region = region_memory
#region = region_null
