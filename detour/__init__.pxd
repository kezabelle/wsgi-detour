import cython

cpdef basestring get_version()


cdef class EntryPoint:
    cdef public wsgi_app
    cdef public short_check  # should match prepare_entrypoint.short_check
    cdef public long_check  # should match prepare_entrypoint.prefix
    cdef public int long_check_length  # should match prepare_entrypoint.long_check_length


@cython.locals(SLASH=str, long_check_length=int)
cdef EntryPoint prepare_entrypoint(int position, prefix, handler)


@cython.locals(entrypoint_config_length=int, position=int, results=list)
cdef list prepare_entrypoints(entrypoints)


cdef class Detour:
    cdef public app
    cdef public list entrypoints

    @cython.locals(entrypoints=list)
    cdef handle(self, environ, start_response)
