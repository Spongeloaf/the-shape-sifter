""" Functions used by the server and the clients"""

# 3rd party imports:
import logging


def create_logger(log_file_const, log_level='DEBUG', log_name='a_logger_has_no_name'):
    """Creates a logger fro the server. Depends on logging module.
    Logger is created with default level set to 'debug'.
    level may be changed later by config files."""

    # Create logger
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file_const, mode='w')      # file handler object for logger
    ch = logging.StreamHandler()                            # create console handler

    ch.setLevel(logging.DEBUG)                              # default log levels set to debug in case config fails
    fh.setLevel(logging.DEBUG)                              # default log levels set to debug in case config fails

    # set levels from config file
    if log_level == 'DEBUG':
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        ch.setLevel(logging.INFO)
        fh.setLevel(logging.INFO)
    elif log_level == 'WARNING':
        ch.setLevel(logging.WARNING)
        fh.setLevel(logging.WARNING)
    elif log_level == 'ERROR':
        ch.setLevel(logging.ERROR)
        fh.setLevel(logging.ERROR)
    elif log_level == 'CRITICAL':
        ch.setLevel(logging.CRITICAL)
        fh.setLevel(logging.CRITICAL)
    else:
        log.critical('Bad logger level set in config file. reverting to "debug" logger')
        log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return log


def log_dump(obj, logger=None):
    """ Dump contents of an object for debugging. If no logger is supplied as a second arg, object is dumped to console."""
    if logger is None:
        for attr in dir(obj):
            if hasattr(obj, attr ):
                print("obj.%s = %s" % (attr, getattr(obj, attr)))
                return
    else:
        for attr in dir(obj):
            if hasattr(obj, attr ):
                logger.critical("obj.%s = %s" % (attr, getattr(obj, attr)))
                return
