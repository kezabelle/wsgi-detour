import cython

cpdef basestring get_version()


cdef class EntryPoint:
    cpdef public wsgi_app
    cpdef public basestring short_check  # should match prepare_entrypoint.short_check
    cpdef public basestring long_check  # should match prepare_entrypoint.prefix
    cpdef public int long_check_length  # should match prepare_entrypoint.long_check_length


@cython.locals(short_check=basestring, starts_with=basestring, SLASH=str, long_check_length=int)
cpdef EntryPoint prepare_entrypoint(int position, basestring prefix, handler)


@cython.locals(entrypoint_config_length=int, position=int, results=list)
cpdef list prepare_entrypoints(entrypoints)


cdef class Detour:
    cpdef public app
    cpdef public list entrypoints

    @cython.locals(path_info=basestring, script_name=basestring, entrypoints=list,
                   short_slice=basestring, short_check=basestring,
                   long_slice=basestring, long_check=basestring)
    cdef handle(self, environ, start_response)
