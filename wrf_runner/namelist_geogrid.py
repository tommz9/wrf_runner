# -*- coding: utf-8 -*-

"""
Contains a structure that holds the rules how to encode the configuration into the various parameters of namelist.wps

The structure is a dict of namelist sections, each section stored as dict or option name and a tuple ( documentation,
format_function )

The format function takes the config dict and formats the appropriate parameters for the namelist.

"""


def list_from_list_of_dict(list_of_dict, key, selector=lambda x: x):
    return [selector(d[key]) for d in list_of_dict]


geogrid_namelist = {
    'share':
        {
            'wrf_core':
                (
                    "WRF_CORE : A character string set to either 'ARW' or 'NMM' that tells the WPS which dynamical core"
                    " the input data are being prepared for. Default value is 'ARW'.",
                    lambda config: 'ARW'),
            'max_dom':
                (
                    "MAX_DOM : An integer specifying the total number of domains/nests, including the parent domain, "
                    "in the simulation. Default value is 1.",
                    lambda config: len(config['domains'])),
            'io_form_geogrid':
                (
                    "IO_FORM_GEOGRID : The WRF I/O API format that the domain files created by the geogrid program will be "
                    "written in. Possible options are: 1 for binary; 2 for NetCDF; 3 for GRIB1. When option 1 is given, "
                    "domain files will have a suffix of .int; when option 2 is given, domain files will have a suffix of "
                    ".nc; when option 3 is given, domain files will have a suffix of .gr1. Default value is 2 ("
                    "NetCDF).",
                    lambda config: 2)
        },
    'geogrid':
        {
            'parent_id':
                (
                    "PARENT_ID :  A list of MAX_DOM integers specifying, for each nest, the domain number of the nest’s "
                    "parent; for the coarsest domain, this variable should be set to 1. Default value is 1.",
                    lambda config: list_from_list_of_dict(config['domains'], 'parent_id')),
            'parent_grid_ratio':
                (
                    "PARENT_GRID_RATIO : A list of MAX_DOM integers specifying, for each nest, the nesting ratio relative "
                    "to the domain’s parent. No default value.",
                    lambda config: list_from_list_of_dict(config['domains'], 'parent_ratio')),
            'i_parent_start':
                (
                    "I_PARENT_START : A list of MAX_DOM integers specifying, for each nest, the x-coordinate of the "
                    "lower-left corner of the nest in the parent unstaggered grid. For the coarsest domain, a value of 1 "
                    "should be specified. No default value.",
                    lambda config: list_from_list_of_dict(config['domains'], 'parent_start', selector=lambda x: x[0])),
            'j_parent_start':
                (
                    "J_PARENT_START : A list of MAX_DOM integers specifying, for each nest, the y-coordinate of the "
                    "lower-left corner of the nest in the parent unstaggered grid. For the coarsest domain, a value of 1 "
                    "should be specified. No default value.",
                    lambda config: list_from_list_of_dict(config['domains'], 'parent_start', selector=lambda x: x[1])),
            'e_we':
                (
                    "E_WE : A list of MAX_DOM integers specifying, for each nest, the nest’s full west-east dimension. For "
                    "nested domains, e_we must be one greater than an integer multiple of the nest's parent_grid_ratio "
                    "(i.e., e_we = n*parent_grid_ratio+1 for some positive integer n). No default value.",
                    lambda config: list_from_list_of_dict(config['domains'], 'size', selector=lambda x: x[0])),
            'e_sn':
                (
                    "E_SN : A list of MAX_DOM integers specifying, for each nest, the nest’s full south-north dimension. "
                    "For nested domains, e_sn must be one greater than an integer multiple of the nest's parent_grid_ratio "
                    "(i.e., e_sn = n*parent_grid_ratio+1 for some positive integer n). No default value.",
                    lambda config: list_from_list_of_dict(config['domains'], 'size', selector=lambda x: x[1])),
            'geog_data_res':
                (
                    "GEOG_DATA_RES : A list of MAX_DOM character strings specifying, for each nest, a corresponding resolution "
                    "or list of resolutions separated by + symbols of source data to be used when interpolating static "
                    "terrestrial data to the nest’s grid. For each nest, this string should contain a resolution matching "
                    "a string preceding a colon in a rel_path or abs_path specification (see the description of GEOGRID.TBL "
                    "options) in the GEOGRID.TBL file for each field. If a resolution in the string does not match any such "
                    "string in a rel_path or abs_path specification for a field in GEOGRID.TBL, a default resolution of data "
                    "for that field, if one is specified, will be used. If multiple resolutions match, the first resolution to "
                    "match a string in a rel_path or abs_path specification in the GEOGRID.TBL file will be used. Default value "
                    "is 'default'.",
                    lambda config: 'default'),
            'dx':
                (
                    "DX : A real value specifying the grid distance in the x-direction where the map scale factor is 1. For "
                    "ARW, the grid distance is in meters for the 'polar', 'lambert', and 'mercator' projection, and in degrees "
                    "longitude for the 'lat-lon' projection; for NMM, the grid distance is in degrees longitude. Grid distances "
                    "for nests are determined recursively based on values specified for parent_grid_ratio and parent_id. "
                    "No default value.",
                    lambda config: config['domains'][0]['step_size'][0]),
            'dy':
                (
                    "DY : A real value specifying the nominal grid distance in the y-direction where the map scale factor "
                    "is 1. For ARW, the grid distance is in meters for the 'polar', 'lambert', and 'mercator' projection, "
                    "and in degrees latitude for the 'lat-lon' projection; for NMM, the grid distance is in degrees latitude. "
                    "Grid distances for nests are determined recursively based on values specified for parent_grid_ratio "
                    "and parent_id. No default value.",
                    lambda config: config['domains'][0]['step_size'][1]),
            'map_proj':
                (
                    "MAP_PROJ : A character string specifying the projection of the simulation domain. For ARW, accepted "
                    "projections are 'lambert', 'polar', 'mercator', and 'lat-lon'; for NMM, a projection of 'rotated_ll' "
                    "must be specified. Default value is 'lambert'.",
                    lambda config: config['projection']['type']),
            'ref_lat':
                (
                    "REF_LAT : A real value specifying the latitude part of a (latitude, longitude) location whose (i,j) "
                    "location in the simulation domain is known. For ARW, ref_lat gives the latitude of the center-point "
                    "of the coarse domain by default (i.e., when ref_x and ref_y are not specified). For NMM, ref_lat always "
                    "gives the latitude to which the origin is rotated. No default value.",
                    lambda config: config['projection']['ref_location'][0]),
            'ref_lon':
                (
                    "REF_LON : A real value specifying the longitude part of a (latitude, longitude) location whose (i, j) "
                    "location in the simulation domain is known. For ARW, ref_lon gives the longitude of the center-point "
                    "of the coarse domain by default (i.e., when ref_x and ref_y are not specified). For NMM, ref_lon always "
                    "gives the longitude to which the origin is rotated. For both ARW and NMM, west longitudes are negative, "
                    "and the value of ref_lon should be in the range [-180, 180]. No default value.",
                    lambda config: config['projection']['ref_location'][1]),
            'truelat1':
                (
                    "TRUELAT1 : A real value specifying, for ARW, the first true latitude for the Lambert conformal projection, "
                    "or the only true latitude for the Mercator and polar stereographic projections. For NMM, truelat1 is ignored. "
                    "No default value.",
                    lambda config: config['projection']['truelat'][0]),
            'truelat2':
                (
                    "TRUELAT2 : A real value specifying, for ARW, the second true latitude for the Lambert conformal conic "
                    "projection. For all other projections, truelat2 is ignored. No default value.",
                    lambda config: config['projection']['truelat'][1]),
            'stand_lon':
                (
                    "STAND_LON : A real value specifying, for ARW, the longitude that is parallel with the y-axis in the Lambert "
                    "conformal and polar stereographic projections. For the regular latitude-longitude projection, this value "
                    "gives the rotation about the earth's geographic poles. For NMM, stand_lon is ignored. No default value.",
                    lambda config: config['projection']['stand_lot']),
            'geog_data_path':
                (
                    "GEOG_DATA_PATH : A character string giving the path, either relative or absolute, to the directory where "
                    "the geographical data directories may be found. This path is the one to which rel_path specifications in "
                    "the GEOGRID.TBL file are given in relation to. No default value.",
                    lambda config: config['data_path'])
        }
}


def config_to_namelist(config):
    output_dict = {}

    for section_name in geogrid_namelist:
        inner_dict = {}

        for option_name in geogrid_namelist[section_name]:
            config_generator = geogrid_namelist[section_name][option_name][1]

            inner_dict[option_name] = config_generator(config)

        output_dict[section_name] = inner_dict

    return output_dict
