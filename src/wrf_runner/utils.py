import f90nml


def get_last_line(file) -> str:
    with open(file, 'r') as f:
        return f.readlines()[-1]


def apply_namelist_patch(template_namelist, output_namelist, patch: dict) -> None:
    f90nml.patch(template_namelist, patch, output_namelist)
