import logging
import subprocess

import f90nml

from .exceptions import WrfRunnerException
from .utils import get_last_line

log = logging.getLogger("wps")


def check_wps_logfile(path_to_file) -> bool:
    return 'Successful completion of program' in get_last_line(path_to_file)


def run_wps_program(program: str) -> None:
    """
    Runs a WPS program and check for success.

    :param program: one of geogrid, ungrib or metgrid
    """
    assert not program.endswith('exe')

    executable = program + '.exe'
    logfile = program + '.log'

    log.info('Starting %s', program)
    run = subprocess.run('./{}'.format(executable), cwd='WPS/')
    log.info('%s finished with return code %i', program, run.returncode)
    if run.returncode or not check_wps_logfile('WPS/{}'.format(logfile)):
        log.error('%s error. Please see the log', program)
        raise WrfRunnerException("Execution of % failed", program)


def run_geogrid():
    return run_wps_program('geogrid')


def run_ungrib():
    return run_wps_program('ungrib')


def run_metgrid():
    return run_wps_program('metgrid')


def create_namelist_patch(initialization_time, length_hours=48) -> dict:
    """
    Create a patch that can be applied on the WPS namelist. This patch modifies the time.

    :param initialization_time: the 'start_date' parameter will be set to this time
    :param length_hours: the 'end_date' parameter will be set to the initialization_time + length_hours
    :return:
    """
    assert length_hours > 0

    # Get number of domains
    nml = f90nml.read('template/namelist.wps')
    domains = nml['share']['max_dom']

    patch = {
        'share': {
            'start_date': [],
            'end_date': []
        }
    }

    # The format for time: '2016-01-01_00:00:00'
    # Arrow                'YYYY-MM-DD_HH:mm:ss'
    time_format = 'YYYY-MM-DD_HH:mm:ss'

    end_time = initialization_time.shift(hours=length_hours)

    patch['share']['start_date'] = [initialization_time.format(time_format)] * domains

    patch['share']['end_date'] = [initialization_time.format(time_format)] * domains
    patch['share']['end_date'][0] = end_time.format(time_format)

    return patch
