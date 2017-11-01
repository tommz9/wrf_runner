
import click

from wrf_runner.wrf_runner import WrfRunner
from wrf_runner.geogrid import Geogrid
from wrf_runner.metgrid import Metgrid
from wrf_runner.ungrib import Ungrib
from wrf_runner.configuration import WpsConfiguration, configuration_dict_from_json


@click.command()
@click.argument('config_file', type=click.Path(exists=True))
def main(config_file):

    runner = WrfRunner()

    configuration = WpsConfiguration(configuration_dict_from_json(config_file))

    geogrid = Geogrid(configuration, log_file='log.txt')
    ungrib = Ungrib(configuration, log_file='log.txt')
    metgrid = Metgrid(configuration, log_file='log.txt')

    runner.add_step(geogrid) \
        .add_step(ungrib) \
        .add_step(metgrid)

    runner.run()


if __name__ == '__main__':
    main()
