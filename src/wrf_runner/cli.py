# -*- coding: utf-8 -*-

import asyncio
import collections
import json
import sys
import traceback

import click
import progressbar

from .geogrid import Geogrid
from .namelist import generate_config_file
from .ungrib import Ungrib


# From: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


@click.group()
def cli():
    """WRF Runner."""
    pass


@cli.group()
def generate():
    pass


@generate.command()
@click.argument('configuration_file')
@click.option('--debug/--no-debug', default=False, help='Prints additional information in the case of an error.')
def wps_namelist(configuration_file, debug):
    """Will generate the WPS namelist"""

    try:
        with open(configuration_file, 'r') as f:
            config = json.load(f)

        geogrid = Geogrid(config)
        ungrib = Ungrib(config)

        namelist = {}
        namelist_geogrid = geogrid.generate_namelist_dict()
        namelist_ungrib = ungrib.generate_namelist_dict()

        dict_merge(namelist, namelist_geogrid)
        dict_merge(namelist, namelist_ungrib)

        click.echo(generate_config_file(namelist))
    except Exception as e:
        click.echo(click.style(str(e), bg='red'))

        if debug:
            click.echo(
                ''.join(traceback.format_exception(None, e, e.__traceback__)))

        sys.exit(1)


@cli.group()
def run():
    pass


@run.command()
@click.argument('configuration_file')
@click.option('--log', default=None, help='Logfile for the output from geogrid')
@click.option('--progress/--no-progress', default=True, help='Turns on/off the progress bar.')
def geogrid(configuration_file, progress, log):
    with open(configuration_file, 'r') as f:
        config = json.load(f)

    if progress:
        widgets = [
            'Finished domains: ',
            progressbar.SimpleProgress(),
            progressbar.Bar(),
            progressbar.Percentage()
        ]

        bar = progressbar.ProgressBar(max_value=2, widgets=widgets)
        bar.initialized = False

        def update_progress_cb(current, out_of):
            if not bar.initialized:
                bar.start()
                bar.initialized = True

            bar.max_value = out_of
            bar.update(current, force=True)

    geogrid = Geogrid(config, progress_update_cb=update_progress_cb if progress else None, print_message_cb=print,
                      log_file=log)

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(geogrid.run())
    loop.close()

    if progress:
        bar.finish()

    if success:
        print('Success.')
        sys.exit(0)
    else:
        print('Failure.')
        sys.exit(1)


@run.command()
@click.argument('configuration_file')
def ungrib(configuration_file):
    with open(configuration_file, 'r') as f:
        config = json.load(f)

    ungrib = Ungrib(config)

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(ungrib.run())
    loop.close()

    if success:
        print('Success.')
        sys.exit(0)
    else:
        print('Failure.')
        sys.exit(1)
