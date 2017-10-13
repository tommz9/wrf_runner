#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Jinja2',
    'jsonschema',
    'click',
    'progressbar2',
    'dateparser'
    # TODO: put package requirements here
]

setup_requirements = [
    'pytest-runner',
    # TODO(tommz9): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    'pytest-mock'
    # TODO: put package test requirements here
]

setup(
    name='wrf_runner',
    version='0.1.0',
    description="Set of tools to run WRF",
    long_description=readme + '\n\n' + history,
    author="Tomas Barton",
    author_email='tomas@tomasbarton.net',
    url='https://github.com/tommz9/wrf_runner',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='wrf_runner',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
