import f90nml
import glob
import logging
import subprocess
import os

from .exceptions import WrfRunnerException

log = logging.getLogger('WRF')


def create_namelist_patch(initialization_time, length_hours=48):
    # Get number of domains
    nml = f90nml.read('template/namelist.wps')
    domains = nml['share']['max_dom']

    patch = {
        'time_control': {
            'start_year': None,
            'start_month': None,
            'start_day': None,
            'start_hour': None,
            'start_minute': None,
            'start_second': None,
            'end_year': None,
            'end_month': None,
            'end_day': None,
            'end_hour': None,
            'end_minute': None,
            'end_second': None
        },
        'domains': {
            'e_we': None,  # directly from WPS namelist
            'e_sn': None,  # directly from WPS namelist
            'e_vert': None,
            'dx': None,
            'dy': None,
            'grid_id': None,  # directly from WPS namelist
            'parent_id': None,  # directly from WPS namelist
            'i_parent_start': None,  # directly from WPS namelist
            'j_parent_start': None,  # directly from WPS namelist
            'parent_grid_ratio': None,  # directly from WPS namelist
            'parent_time_step_ratio': None,
            'max_dom': None
        }
    }

    patch['time_control']['start_year'] = [initialization_time.year] * domains
    patch['time_control']['start_month'] = [initialization_time.month] * domains
    patch['time_control']['start_day'] = [initialization_time.day] * domains

    patch['time_control']['start_hour'] = [initialization_time.hour] * domains
    patch['time_control']['start_minute'] = [initialization_time.minute] * domains
    patch['time_control']['start_second'] = [initialization_time.second] * domains

    end_time = initialization_time.shift(hours=length_hours)

    patch['time_control']['end_year'] = [end_time.year] * domains
    patch['time_control']['end_month'] = [end_time.month] * domains
    patch['time_control']['end_day'] = [end_time.day] * domains

    patch['time_control']['end_hour'] = [end_time.hour] * domains
    patch['time_control']['end_minute'] = [end_time.minute] * domains
    patch['time_control']['end_second'] = [end_time.second] * domains

    for variable in ['e_we', 'e_sn', 'parent_id', 'i_parent_start', 'j_parent_start', 'parent_grid_ratio']:
        patch['domains'][variable] = nml['geogrid'][variable]

    patch['domains']['grid_id'] = list(range(1, domains + 1))
    patch['domains']['parent_time_step_ratio'] = nml['geogrid']['parent_grid_ratio']

    wrf_nml = f90nml.read('template/namelist.input')

    vertical_levels = wrf_nml['domains']['e_vert'][0]
    patch['domains']['e_vert'] = [vertical_levels] * domains

    wps_dx = nml['geogrid']['dx']

    try:
        wps_dx = wps_dx[0]
    except TypeError:
        pass

    new_dx = [wps_dx]
    for i in range(1, domains):
        new_dx.append(new_dx[-1] / patch['domains']['parent_grid_ratio'][i])

    patch['domains']['dx'] = new_dx
    patch['domains']['dy'] = new_dx

    patch['domains']['max_dom'] = domains

    return patch


def link_metgrid_outputs(src, dst):
    dst_files = glob.glob(dst + '/met_em.*.nc')
    if dst_files:
        log.info('Removing {} old links from "{}"'.format(len(dst_files), dst))
        for link in dst_files:
            os.unlink(link)

    log.info('Linking in the metgrid output.')
    src_files = glob.glob(src + '/met_em.*.nc')
    log.info('{} files found in "{}"'.format(len(src_files), src))

    for file in src_files:
        basename = os.path.basename(file)
        os.symlink(os.path.abspath(file), dst + '/' + basename)

    log.info('Files linked')


def check_wrf_output():
    with open('WRF/rsl.error.0000') as f:
        last_line = f.readlines()[-1]
        return 'SUCCESS COMPLETE' in last_line


def run_real():
    log.info('Starting real.exe')
    run = subprocess.run(['mpirun', '-n', '1', './real.exe'], cwd='WRF/')
    log.info('real.exe finished with return code %i', run.returncode)

    if run.returncode or not check_wrf_output():
        log.error('real.exe failed. Please see the log')
        raise WrfRunnerException('real.exe failed.')


def run_wrf(cores):
    log.info('Starting wrf.exe')
    run = subprocess.run(['mpirun', '-n', str(cores), './wrf.exe'], cwd='WRF/')
    log.info('wrf.exe finished with return code %i', run.returncode)

    if run.returncode or not check_wrf_output():
        log.error('wrf.exe failed. Please see the log')
        raise WrfRunnerException('wrf.exe failed.')
