==========
WRF Runner
==========

Tools to configure, run and monitor the Weather Research and Forecasting model (WRF).

The idea behind this project is to create a (web) interface for WRF that could be added to a docker container together with WRF that would allow to configure the model, run it and monitoring the progress from this interface without having to touch the config files. It will also have an API that would allow to send the configuraiton from a script so that bigger scale simmulations consisting of many runs could be run this way. 

* Free software: MIT license

(Planed) Features
--------

Most of these is not done as long as this message is here.

* Configure the software. Use a simpler configuration schema then the oldschool namelist files.
* Run the software and show the progress.
* Save the logs
* on-the-fly processing of the output files. Allow to run precessing scripts on the files as soon as the files are saved.
* web interface

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

