#!./venv/bin/python
import click
import logging
import arrow
import pathlib
import shutil
import subprocess
import glob
import os
import sys

from wrf_runner import wps, wrf, utils
from wrf_runner.linkgrib import link_grib
from wrf_runner.datasets.nam import NAM_forecast, NAM

log = logging.getLogger('job')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s --- %(message)s')

WRF_INSTALL = pathlib.Path('/home/tbarton/wrf/3.9.1.1')
WRF_PATH = WRF_INSTALL / 'WRFV3'
WPS_PATH = WRF_INSTALL / 'WPS'


@click.command()
@click.argument("initialization_folder", type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--run-wps/--no-run-wps', default=True)
@click.option('--geogrid/--no-geogrid', default=True)
@click.option('--ungrib/--no-ungrib', default=True)
@click.option('--metgrid/--no-metgrid', default=True)
@click.option('--copy-wrf/--no-copy-wrf', default=True)
@click.option('--real/--no-real', default=True)
@click.option('--run-wrf/--no-run-wrf', default=True)
@click.option('--simulation-time', default=54)
def main(initialization_folder, run_wps, geogrid, ungrib, metgrid, copy_wrf, real, run_wrf, simulation_time):
    log.info('Starting. Initialization folder "%s"', initialization_folder)

    initialization_folder = pathlib.Path(initialization_folder)
    nam_forecast = NAM_forecast(initialization_folder)   

    initialization_time = nam_forecast.dataset_start

    log.info('Initialization time of the forecast: %s', initialization_time)
    
    spinup_start = initialization_time.shift(hours=-6)

    # Copy the WPS and WRF software into the working directory
    if copy_wrf:
        shutil.rmtree('WPS', ignore_errors=True)
        log.info('Getting WPS from "%s"', WPS_PATH)
        shutil.copytree(str(WPS_PATH), 'WPS')
        log.info('WPS Copied')

        shutil.rmtree('./WRF', ignore_errors=True)
        log.info('Getting WRF from "%s"', WRF_PATH)
        shutil.copytree(str(WRF_PATH), 'WRF')
        log.info('WRF Copied')

    geogrid = run_wps and geogrid
    ungrib = run_wps and ungrib
    metgrid = run_wps and metgrid

    # Instantiate the WPS Configuration
    if geogrid or ungrib or metgrid:
        wps_patch = wps.create_namelist_patch(spinup_start, length_hours=simulation_time)
        utils.apply_namelist_patch('template/namelist.wps', 'WPS/namelist.wps', wps_patch)
        shutil.copy('template/Vtable', 'WPS/')

    # GEOGRID
    if geogrid:
        wps.run_geogrid()

    # UNGRIB
    if ungrib:
        log.info('Linking in the meteo data')

        # Get the spinup data file from NAM analysis
        nam = NAM('/fileserver1/datasets/NAM/analysis/2016/')
        spinup_files =  nam.dates[spinup_start]
        link_grib(spinup_files)

        link_grib(initialization_folder.glob('*.grb2'), delete_links=False)
        
        wps.run_ungrib()

    # METGRID
    if metgrid:
        wps.run_metgrid()

    if real or run_wrf:
        wrf_patch = wrf.create_namelist_patch(spinup_start, length_hours=simulation_time)
        utils.apply_namelist_patch('template/namelist.input', 'WRF/namelist.input', wrf_patch)
        shutil.copy('template/tslist', 'WRF/')

    if real:
        wrf.link_metgrid_outputs('WPS/', 'WRF/')
        wrf.run_real()

    if run_wrf:
        wrf.run_wrf(12)

    log.info('Done')


if __name__ == '__main__':
    main()
