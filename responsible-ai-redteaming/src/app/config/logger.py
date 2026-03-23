'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''



import datetime
import logging
import os
import sys
from typing import Optional  
from .config import read_config


class CustomLogger(logging.Logger):  


    def __init__(self):

        """Create a custom logger with the specified `name`. When `log_dir` is None, a simple
        console logger is created. Otherwise, a file logger is created in addition to the console
        logger.

        By default, the five standard logging levels (DEBUG through CRITICAL) only display
        information in the log file if a file handler is added to the logger, but **not** to the
        console.
        :param name: name for the logger
        :param verbose: bool: whether the logging should be verbose; if True, then all messages get
            logged both to stdout and to the log file (if `log_dir` is specified); if False, then
            messages only get logged to the log file (if `log_dir` is specified)
        :param log_dir: str: (optional) the directory for the log file; if not present, no log file
            is created
        """
        # Create custom logger logging all five levels
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_cfg_path = os.path.join(BASE_DIR, 'logger.ini')
        log_params = read_config('logDetails', log_cfg_path)

        raw_name = log_params.get('file_name') or 'application_logger'  # ensure non-None
        name = str(raw_name)

        verbose_raw = str(log_params.get('verbose', 'False')).strip().lower()
        verbose = verbose_raw in ('true', '1', 'yes')

        log_dir_raw = log_params.get('log_dir', '')
        log_dir = os.path.normpath(str(log_dir_raw).strip()) if log_dir_raw else ''
        self.log_dir = log_dir  
        super().__init__(name) 
        self.setLevel(logging.DEBUG)

        # Add new logging level
        logging.addLevelName(logging.INFO, 'INFO')

        # Determine verbosity settings
        self.verbose = verbose

        # Create stream handler for logging to stdout (log all five levels)
        self.stdout_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        self.stdout_handler.setLevel(logging.DEBUG)
        self.stdout_handler.setFormatter(logging.Formatter('%(message)s'))
        self.enable_console_output()

        self.file_handler: Optional[logging.FileHandler] = None
        if self.log_dir:
            self.add_file_handler(name, self.log_dir)



    def add_file_handler(self, name: str, log_dir: str) -> None:

        """Add a file handler for this logger with the specified `name` (and store the log file
        under `log_dir`)."""
        # Format for file log
        fmt = '%(asctime)s | %(levelname)9s | %(filename)s:%(lineno)d | %(message)s'
        formatter = logging.Formatter(fmt)

        # Determine log path and file name; create log path if it does not exist
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_name = f'{str(name).replace(" ", "_")}_{now}'
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as exc:  
                print(f'{self.__class__.__name__}: Cannot create directory {log_dir}. ', end='', file=sys.stderr)
                print(f'Reason: {exc}', file=sys.stderr)
                log_dir = '/tmp' if sys.platform.startswith('linux') else '.'
                print(f'Defaulting to {log_dir}.', file=sys.stderr)
        log_file = os.path.join(log_dir, log_name) + '.log'

        # Create file handler for logging to a file (log all five levels)
        try:
            fh = logging.FileHandler(log_file)
        except OSError as exc:  # PermissionError covered
            print(f'{self.__class__.__name__}: Cannot open log file {log_file}.', file=sys.stderr)
            print(f'Reason: {exc}', file=sys.stderr)
            return
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.file_handler = fh
        self.addHandler(fh)



    def has_console_handler(self) -> bool:

        return any(isinstance(h, logging.StreamHandler) for h in self.handlers)



    def has_file_handler(self) -> bool:

        return any(isinstance(h, logging.FileHandler) for h in self.handlers)



    def disable_console_output(self):
        if not hasattr(self, "stdout_handler"):
            return
        if not self.has_console_handler():
            return
        self.removeHandler(self.stdout_handler)



    def enable_console_output(self):

        if self.has_console_handler():
            return
        self.addHandler(self.stdout_handler)



    def disable_file_output(self) -> None:

        if self.file_handler and self.has_file_handler():
            self.removeHandler(self.file_handler)

    def enable_file_output(self) -> None:

        if self.file_handler and not self.has_file_handler():
            self.addHandler(self.file_handler)



    def framework(self, msg, *args, **kwargs):

        """Logging method for the FRAMEWORK level. The `msg` gets logged both to stdout and to file
        (if a file handler is present), irrespective of verbosity settings."""

        return super().info(msg, *args, **kwargs)
    


    def _custom_log(self, func, msg, *args, **kwargs) -> None:

        """Helper method for logging DEBUG through CRITICAL messages by calling the appropriate
        `func()` from the base class."""
        # Log normally if verbosity is on
        if self.verbose:
            return func(msg, *args, **kwargs)

       
        if not self.has_file_handler():
            return

       
        self.disable_console_output()
        func(msg, *args, **kwargs)
        self.enable_console_output()



    def debug(self, msg, *args, **kwargs):
        
        self._custom_log(super().debug, msg, *args, **kwargs)



    def info(self, msg, *args, **kwargs):

        self._custom_log(super().info, msg, *args, **kwargs)



    def warning(self, msg, *args, **kwargs):

        self._custom_log(super().warning, msg, *args, **kwargs)



    def error(self, msg, *args, **kwargs):

        self._custom_log(super().error, msg, *args, **kwargs)



    def critical(self, msg, *args, **kwargs):

        self._custom_log(super().critical, msg, *args, **kwargs)

        


if __name__ == "__main__":
    CustomLogger()
    CustomLogger()
