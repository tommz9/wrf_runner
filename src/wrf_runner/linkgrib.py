import glob
import os
import logging

log = logging.getLogger('linkgrib')


def grib_alphabetical_extensions():
    """
    Generate file extensions AAA, AAB, AAC, ...
    """

    current = 'AAA'
    yield current

    while current != 'ZZZ':
        numbers = [ord(c) for c in current]

        numbers[2] += 1

        if numbers[2] > ord('Z'):
            numbers[2] = ord('A')
            numbers[1] += 1
            if numbers[1] > ord('Z'):
                numbers[1] = ord('A')
                numbers[0] += 1

        current = ''.join(map(chr, numbers))

        yield current


def link_grib(files, filter_function=None) -> None:
    """
    Link the data files into the working directory.

    Python implementation of the script linkgrib

    :param files: a list of files to link or a pattern used for globing
    :param filter_function: this function can be used to filter the linked files
    """

    # Delete all links
    current_links = glob.glob('WPS/GRIBFILE.???')

    for link in current_links:
        os.remove(link)

    # Get the new files
    if isinstance(files, str):
        new_files = glob.glob(files)
    else:
        new_files = files

    if filter_function:
        new_files = filter(filter_function, new_files)

    # Link the new paths
    for extension, new_file in zip(grib_alphabetical_extensions(), sorted(new_files)):
        log.debug('Linking: %s', new_file)
        os.symlink(str(new_file), 'WPS/GRIBFILE.' + extension)
