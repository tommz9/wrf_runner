# Usage ideas

This is a design document with ideas about how this package should be used.

## Simple use case

Simple use case:

```python

from wrf_runner import WrfRunner, Ungrib, Geogrid, Metgrid
from wrf_runner.wps import Ungrib, Geogrid, Metgrid
from wrf_runner.wrf import Real, Wrf
from wrf_runner.utils import extract_variables, collect_logs, delete_output_files, link_files

runner = WrfRunner()
runner.enable_web_monitor(port=8080)

ungrib = Ungrib()
geogrid = Geogrid()
metgrid = Metgrid()

real = Real()
wrf = Wrf()

data_extractor = extract_variables(
    source=wrf.output_files,
    variables=['TC'],
    times='all',
    location=(49.33, 113.2))

runner.add_step(ungrib)
      .add_step(geogrib)
      .add_step(metgrid)
      .add_step(collect_logs(ungrib, geogrid, metgrid))
      .add_step(delete_output_files(ungrib.output_files, geogrid.output_files))
      .add_step(link_files(metgrid.output_files, real.working_directory))
      .add_step(real)
      .add_step(wrf)
      .add_step(data_extractor)

runner.run()

```

The idea is to be able to run the entire WRF pipeline and monitor the progress. The steps will be
registered in the runner that will run all of them in order. Each step is a coroutine.

The runner will show the progress on the command line. Alternatively, it will start a web-server
where the progress can be monitored.

## Configuration

There are several things that need to be configured:

* location of the software (WRFV3 and WPS directories)
* directory with input files
  * configuration for programs
  * vtables ...
* directory for outputs and log files

WRF and WPS could have separate configuration files.  