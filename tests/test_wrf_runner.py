#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `wrf_runner` package."""

import pytest

from wrf_runner import wrf_runner
from wrf_runner import WrfException

class TestConfiguration:

    @pytest.mark.parametrize("config", [{}, 5, 'nonsense'])
    def test_basic_wrong(self, config):
        with pytest.raises(WrfException):
            wrf_runner.check_configuration(config)
