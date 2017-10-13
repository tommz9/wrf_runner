# -*- coding: utf-8 -*-
import logging
import asyncio
from contextlib import closing
from types import SimpleNamespace


async def stream_reader(stream, callback):
    """
    Awaits on the stream and runs the callback for each line.
    :param callback: callable expecting the line as a string
    """
    while True:
        line = await stream.readline()
        if line:
            callback(line.decode('ASCII').strip())
        else:
            return


class Program:
    """
    Base class for runable WPS and WRF programs.

    Responsibilities:

    * Run the program
    * Listen for output on stderr and stdout
    * Pass the output to configured callbacks
    * Log the output
    * Return the retval

    """

    def __init__(self,
                 executable,
                 stdout_callback,
                 stderr_callback,
                 log_file=None):
        """
        :param executable: path to the program executable
        :param stdout_callback: a function that will be called for each line of stdout
        :param stderr_callback: a function that will be called for each line of stderr 
        :param log_file: The stdout and stderr will be saved to this file
        """

        self.executable = executable
        self.log_file = log_file

        self.stderr_callback = stderr_callback
        self.stdout_callback = stdout_callback
        self.logger = None

    def initialize_logger(self):
        """
        Prepares the stderr and stdout logger if the log filename is provided

        returns the file handler that can be closed or a dummy object with a close
        method that does nothing
        """

        if self.log_file:
            self.logger = logging.Logger(self.executable)

            file_handler = logging.FileHandler(self.log_file)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

            return file_handler

        return SimpleNamespace(close=lambda: None)

    async def run(self):
        """
        Listens on the stdout and stderr and runs the callbacks for each line.
        """

        with closing(self.initialize_logger()):
            # Run the program
            process = await asyncio.create_subprocess_exec(
                self.executable,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            # Setup the line callbacks
            await stream_reader(process.stdout, self.private_stdout_callback)
            await stream_reader(process.stderr, self.private_stderr_callback)

            # Wait for the program to end
            return await process.wait()

    def private_stderr_callback(self, line):
        """
        Is called by the async reader. Logs the line if the log file was configured and
        pass the line to the callback
        """
        if self.logger:
            self.logger.error(line)
        self.stderr_callback(line)

    def private_stdout_callback(self, line):
        """
        Is called by the async reader. Logs the line if the log file was configured and
        pass the line to the callback
        """
        if self.logger:
            self.logger.info(line)
        self.stdout_callback(line)
