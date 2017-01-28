from typing import Callable, Iterable, Tuple

MountList = Iterable[Tuple[str, Callable]]
WSGIOutput = Iterable[bytes]

class EntryPoint:
    def __init__(self, wsgi_app, short_check: str, long_check: str, long_check_length: int): ...

def prepare_entrypoint(position: int, prefix: str, handler: Callable) -> EntryPoint: ...

def prepare_entrypoints(entrypoints: MountList) -> list: ...

class Detour:
    def __init__(self, app: Callable[[str, int],int], mounts: MountList): ...
