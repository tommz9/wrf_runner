import arrow
import glob

import click

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

        self.dates = {NAM.filename_to_datetime(file): file for file in self.data_files}

        self.dataset_start = min(self.dates.keys())
        self.dataset_end = max(self.dates.keys())

    def check_complete(self):

        date_to_check = self.dataset_start

        while date_to_check <= self.dataset_end:
            if date_to_check not in self.dates:
                raise WrfRunnerException('Dataset not complete. % date is missing', date_to_check)
            date_to_check = date_to_check.shift(hours=NAM.time_step)


@click.command()
@click.argument('path_to_dataset')
def main(path_to_dataset):
    nam = NAM(path_to_dataset)

    print('Dataset opened')
    print('Dataset folder:   {}'.format(nam.folder))
    print('Dataset timestep: {}'.format(NAM.time_step))
    print('Dataset start:    {}'.format(nam.dataset_start))
    print('Dataset end:      {}'.format(nam.dataset_end))


if __name__ == '__main__':
    main()
