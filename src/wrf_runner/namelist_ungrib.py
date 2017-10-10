# -*- coding: utf-8 -*-

ungrib_namelist = {
    'share': {
        'start_date':
            (
                "START_DATE : A list of MAX_DOM character strings of the form 'YYYY-MM-DD_HH:mm:ss' specifying the "
                "starting UTC date of the simulation for each nest. The start_date variable is an alternate to "
                "specifying start_year, start_month, start_day, and start_hour, and if both methods are used for "
                "specifying the starting time, the start_date variable will take precedence. No default value.",
                lambda config: config['start_date'].strftime("%Y-%m-%d_%H:%M:%S")
            ),
        'end_date':
            (
                "END_DATE : A list of MAX_DOM character strings of the form 'YYYY-MM-DD_HH:mm:ss' specifying the "
                "ending UTC date "
                "of the simulation for each nest. The end_date variable is an alternate to specifying end_year, end_"
                "month, end_day, and end_hour, and if both methods are used for specifying the ending time, the end_"
                "date variable will take precedence. No default value.",
                lambda config: config['end_date'].strftime("%Y-%m-%d_%H:%M:%S")
            ),
        'interval_seconds':
            (
                "INTERVAL_SECONDS : The integer number of seconds between time-varying meteorological input files. "
                "No default value.",
                lambda config: config['interval']
            )
    },
    'ungrib': {
        'out_format':
            (
                "OUT_FORMAT : A character string set either to 'WPS', 'SI', or 'MM5'. If set to 'MM5', ungrib will "
                "write output in the format of the MM5 pregrid program; if set to 'SI', ungrib will write output "
                "in the format of grib_prep.exe; if set to 'WPS', ungrib will write data in the WPS intermediate "
                "format. Default value is 'WPS'.",
                lambda config: 'WPS'
            ),
        'prefix':
            (
                "PREFIX : A character string that will be used as the prefix for intermediate-format files created by "
                "ungrib; here, prefix refers to the string PREFIX in the filename PREFIX:YYYY-MM-DD_HH of an "
                "intermediate file. The prefix may contain path information, either relative or absolute, in which "
                "case the intermediate files will be written in the directory specified. This option may be useful "
                "to avoid renaming intermediate files if ungrib is to be run on multiple sources of GRIB data. Default "
                "value is 'FILE'.",
                lambda config: 'FILE'
            )
    }
}


def config_to_namelist(config):
    output_dict = {}

    for section_name in ungrib_namelist:
        inner_dict = {}

        for option_name in ungrib_namelist[section_name]:
            config_generator = ungrib_namelist[section_name][option_name][1]

            inner_dict[option_name] = config_generator(config)

        output_dict[section_name] = inner_dict

    return output_dict
