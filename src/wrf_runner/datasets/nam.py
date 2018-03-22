import glob
import os

import click
import arrow
import re

from ..exceptions import WrfRunnerException


class NAM:
    time_step = 6
    dx = 12

    def __init__(self, folder):
        self.folder = folder

        self.data_files = None
        self.dates = None
        self.dataset_start = None
        self.dataset_end = None

        self.scan_folder()
        self.check_complete()

    @staticmethod
    def filename_to_datetime(filename):
        # The format of the filename: "nam_218_20160101_1200_000.grb2"
        return arrow.get(str(filename), 'YYYYMMDD_HHmm')

    def scan_folder(self):
        self.data_files = glob.glob(self.folder + '/nam_218_*.grb2')

        self.dates = {}
        for file in self.data_files:
            datetime = NAM.filename_to_datetime(file)
            try:
                self.dates[datetime].append(file)
            except KeyError:
                self.dates[datetime] = [file]

        self.dataset_start = min(self.dates.keys())
        self.dataset_end = max(self.dates.keys())

    def check_complete(self):

        date_to_check = self.dataset_start

        while date_to_check <= self.dataset_end:
            if date_to_check not in self.dates:
                raise WrfRunnerException('Dataset not complete. % date is missing', date_to_check)
            date_to_check = date_to_check.shift(hours=NAM.time_step)


class NAM_forecast:
    time_step = 1
    dx = 12

    def __init__(self, folder):
        self.folder = str(folder)

        self.data_files = None
        self.dates = None
        self.dataset_start = None
        self.dataset_end = None

        self.scan_folder()

    def scan_folder(self):
        self.data_files = glob.glob(self.folder + '/nam_218_*.grb2')

        self.dates = {NAM_forecast.filename_to_datetime(file): file for file in self.data_files}

        self.dataset_start = min(self.dates.keys())
        self.dataset_end = max(self.dates.keys())

    @staticmethod
    def filename_to_datetime(filename):
        # The format of the filename: "nam_218_20160117_0600_005.grb2"
        # last three digits are the time shift

        filename = os.path.basename(filename)
        datetime = arrow.get(str(filename), 'YYYYMMDD_HHmm')

        parser = r'nam_218_.*_.*_(\d\d\d)\.grb2'
        result = re.match(parser, filename)
        hours = int(result.group(1))

        return datetime.shift(hours=hours)


@click.command()
@click.argument('path_to_dataset')
@click.option('--forecast/--no-forecast', default=False)
def main(path_to_dataset, forecast):
    if forecast:
        nam = NAM_forecast(path_to_dataset)
    else:
        nam = NAM(path_to_dataset)

    print('Dataset opened')

    print('Dataset folder:   {}'.format(nam.folder))
    print('Dataset timestep: {}'.format(NAM.time_step))
    print('Dataset start:    {}'.format(nam.dataset_start))
    print('Dataset end:      {}'.format(nam.dataset_end))


if __name__ == '__main__':
    main()
