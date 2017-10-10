import pytest
from wrf_runner import WrfException
from wrf_runner import namelist
from wrf_runner.ungrib import check_config, Ungrib


@pytest.mark.parametrize("invalid_config", [{}, '', 45])
def test_check_config_fails_simple(invalid_config):
    with pytest.raises(WrfException):
        check_config(invalid_config)


invalid_samples = [
    {
        # 'start_date': '2017-09-10',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '2017-09-10',
        # 'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    },
    {
        'start_date': '2017-09-10',
        'end_date': 'what?',
        'interval': 3600,
        'prefix': 'FILE'
    }
]


@pytest.mark.parametrize("invalid_config", invalid_samples)
def test_check_config_fails(invalid_config):
    with pytest.raises(WrfException):
        check_config(invalid_config)


valid_samples = [
    {
        'start_date': '2017-09-10',
        'end_date': '2017-09-11',
        'interval': 3600,
        'prefix': 'FILE'
    }
]


@pytest.mark.parametrize("valid_config", valid_samples)
def test_check_valid_config(valid_config):
    check_config(valid_config)


@pytest.mark.parametrize("valid_config", valid_samples)
def test_accepted_by_namelist_generator(valid_config):
    ungrib = Ungrib(valid_config)
    X = ungrib.generate_namelist_dict()
    config_file = namelist.generate_config_file(X)
    print(config_file)
