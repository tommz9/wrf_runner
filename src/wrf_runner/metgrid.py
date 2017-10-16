
from typing import Callable

from .wrf_runner import system_config

class Metgrid:
    def __init__(self,
                config,
                progress_update_cb: Callable[[int, int], None] = None,
                print_message_cb: Callable[[str], None] = None,
                log_file=None):
        pass

    async def run(self):
        pass