# -*- coding: utf-8 -*-
"""
Code to convert the namelist in a dictionary form into a proper namelist.wps file format.
"""

from jinja2 import Environment, DictLoader

loader = DictLoader({
    'macros': """\
{% macro make_line(key, value) %}\
{{ key }} = \
{% if value is string %}'{{ value}}'\
{% elif value is iterable %}{{ value|join(', ') }}\
{% else %}{{ value }}{% endif %}\
{%- endmacro %}


{% macro make_section(name, items) -%}
&{{ name }}
{% for key, value in items.items() %}\
 {{ make_line(key, value) }}
{% endfor -%}
/
{%- endmacro %}

{% macro make_file(items) -%}
{% for key, value in items.items() %}\
{{ make_section(key, value) }}
{{- "\n" if not loop.last }}
{% endfor -%}
{%- endmacro %}

""",
    'line_template': '{%from \'macros\' import make_line%}{{ make_line(key, value) }}',
    'section_template': '{%from \'macros\' import make_section%}{{ make_section(name, items) }}',
    'file_template': '{%from \'macros\' import make_file%}{{ make_file(items) }}'
})

environment = Environment(loader=loader)

#: creates one line in the configuration file
#: takes a 'key' and 'value' parameters and outputs
#: "key = value"
#: Works for strings, numbers and lists of numbers
line_template = environment.get_template('line_template')

#: generates an entire section 'name'
#: takes 'name' and 'items' where items is a dict like where the key and value are passed to line_template
section_template = environment.get_template('section_template')

#: generates the entire config file. Take a dict of sections (section_name, section_dict) in the parameter 'items'
file_template = environment.get_template('file_template')


def generate_config_file(config):
    """
    Converts a dictionary of configuration options into a config file formatted for WPS or WRF

    :param config: a dictionary of configuration section. Section name is stored as the key, value stores another
    dictionary of (config_name, config_values).
    :return: string with the content of the config file
    """

    return file_template.render(items=config)
