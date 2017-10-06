import pytest

from collections import OrderedDict

from wrf_runner.namelist import line_template, section_template, file_template, generate_config_file

line_template_examples = [
    ('parent_id', 2, 'parent_id = 2'),
    ('parent_id', [1, 1, 2], 'parent_id = 1, 1, 2'),
    ('map_proj', 'lambert', 'map_proj = \'lambert\''),
]


@pytest.mark.parametrize("key, value, expected", line_template_examples)
def test_line_template(key, value, expected):
    assert (line_template.render(key=key, value=value) == expected)


# items has to be ordered for the test
section_template_examples = [
    ('geogrid', OrderedDict([
        ('parent_id', [1, 1, 2]),
        ('e_sn', [100, 100, 100]),
        ('map_proj', 'lambert'),
        ('truelat2', 51.57)]), '''\
&geogrid
 parent_id = 1, 1, 2
 e_sn = 100, 100, 100
 map_proj = 'lambert'
 truelat2 = 51.57
/''')
]


@pytest.mark.parametrize("name, items, expected", section_template_examples)
def test_section_template(name, items, expected):
    result = section_template.render(name=name, items=items)
    assert (result == expected)


file_template_examples = [
    (OrderedDict([
        ('share', OrderedDict([
            ('parent_id', [1, 1, 2]),
            ('e_sn', [100, 100, 100]),
            ('map_proj', 'lambert'),
            ('truelat2', 51.57)])),
        ('geogrid', OrderedDict([
            ('parent_id', [1, 1, 2]),
            ('e_sn', [100, 100, 100]),
            ('map_proj', 'lambert'),
            ('truelat2', 51.57)]))]), '''\
&share
 parent_id = 1, 1, 2
 e_sn = 100, 100, 100
 map_proj = 'lambert'
 truelat2 = 51.57
/

&geogrid
 parent_id = 1, 1, 2
 e_sn = 100, 100, 100
 map_proj = 'lambert'
 truelat2 = 51.57
/
''')
]


@pytest.mark.parametrize("items, expected", file_template_examples)
def test_file_template(items, expected):
    result = file_template.render(items=items)
    assert (result == expected)


@pytest.mark.parametrize("config, expected", file_template_examples)
def test_generate_config_file(config, expected):
    result = generate_config_file(config)
    assert (result == expected)
