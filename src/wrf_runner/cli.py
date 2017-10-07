# -*- coding: utf-8 -*-

import json
import sys
import traceback

import click

from .geogrid import Geogrid
from .namelist import generate_config_file


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

        namelist = geogrid.generate_namelist_dict()

        click.echo(generate_config_file(namelist))
    except Exception as e:
        click.echo(click.style(str(e), bg='red'))

        if debug:
            click.echo(''.join(traceback.format_exception(None, e, e.__traceback__)))

        sys.exit(1)
