#log.py
import logging
import logging.handlers
import sys
import config


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging():

    formatter = logging.Formatter(
        #fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt=DATE_FORMAT
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    try:
        logfile_filename = config.general.log_file
        logfile_level = config.general.log_level

        # Log to file
        fileHandler = logging.handlers.RotatingFileHandler(
            logfile_filename,
            maxBytes=(1024 * 1024 * 10),  # 10 MB
            backupCount=10,
        )
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(logfile_level)
        logger.addHandler(fileHandler)
    except Exception as err:
        print 'WARNING: No log file is being saved: ' + err.message
        # Log to stdout
        stdoutHandler = logging.StreamHandler(sys.stdout)
        stdoutHandler.setFormatter(formatter)
        logger.addHandler(stdoutHandler)

    return logger

logger = setup_logging()



