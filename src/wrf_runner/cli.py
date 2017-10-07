# -*- coding: utf-8 -*-

import json
import sys

import click

from .geogrid import Geogrid
from .namelist import generate_config_file


@click.group()
def cli():
    """WRF Runner."""


@click.group()
def generate():
    pass


@click.command()
@click.argument('configuration_file')
def wps_namelist(configuration_file):
    """Will generate the WPS namelist"""

    try:
        with open(configuration_file, 'r') as f:
            config = json.load(f)

        geogrid = Geogrid(config)

        namelist = geogrid.generate_namelist_dict()

        click.echo(generate_config_file(namelist))
    except Exception as e:
        click.echo(click.style(str(e), bg='red'))
        sys.exit(1)


cli.add_command(generate)
generate.add_command(wps_namelist)
