"""
Lookout

This is the main control script for the Lookout garden monitor.

Some day, there will be more text here...
"""

import time
import logging as log

# Must set up logger before importing our own modules or it won't work properly
log.basicConfig(format = "%(asctime)s [%(levelname)s] %(message)s", datefmt = "%d-%m-%Y %I:%M:%S %p", level = log.INFO)
log.info("*** Lookout started ***")

import gpio_manager as gpio

### Constants ###



### Setup ###

log.info("Something happened")
log.warning("Something bad happened!")