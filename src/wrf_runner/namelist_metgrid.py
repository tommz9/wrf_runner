

metgrib_namelist = {
    'metgrid': {
        'fg_name': (
            'FG_NAME : A list of character strings specifying the path and prefix '
            'of ungribbed data files. The path may be relative or absolute, and '
            'the prefix should contain all characters of the filenames up to, but' 
            'not including, the colon preceding the date. When more than one fg_name' 
            'is specified, and the same field is found in two or more input sources,' 
            'the data in the last encountered source will take priority over all'
            'preceding sources for that field. Default value is an empty list (i.e.,' 
            'no meteorological fields).',
            lambda config: 'FILE'
        ),
        'io_form_metgrid': (
            ' IO_FORM_METGRID : The WRF I/O API format that the output created by the '
            'metgrid program will be written in. Possible options are: 1 for binary; 2 ' 
            'for NetCDF; 3 for GRIB1. When option 1 is given, output files will have a ' 
            'suffix of .int; when option 2 is given, output files will have a suffix '
            'of .nc; when option 3 is given, output files will have a suffix of .gr1. '
            'Default value is 2 (NetCDF).',
            lambda config: 2
        )
    }
}

def config_to_namelist(config):
    output_dict = {}

    for section_name in metgrib_namelist:
        inner_dict = {}

        for option_name in metgrib_namelist[section_name]:
            config_generator = metgrib_namelist[section_name][option_name][1]

            inner_dict[option_name] = config_generator(config)

        output_dict[section_name] = inner_dict

    return output_dict
