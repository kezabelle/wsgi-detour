import cython

cpdef str get_version()


cdef class EntryPoint:
    cpdef public wsgi_app
    cpdef public str short_check  # should match prepare_entrypoint.short_check
    cpdef public str long_check  # should match prepare_entrypoint.prefix
    cpdef public int long_check_length  # should match prepare_entrypoint.long_check_length


@cython.locals(short_check=str, starts_with=str, SLASH=str, long_check_length=int)
cpdef EntryPoint prepare_entrypoint(int position, str prefix, handler)


@cython.locals(entrypoint_config_length=int, position=int, results=list)
cpdef list prepare_entrypoints(entrypoints)


cdef class Detour:
    cpdef public app
    cpdef public list entrypoints

    @cython.locals(path_info=str, script_name=str, entrypoints=list,
                   short_slice=str, short_check=str, long_slice=str,
                   long_check=str)
    cdef handle(self, environ, start_response)
