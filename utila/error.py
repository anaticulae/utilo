#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================
from contextlib import contextmanager

from utila.logging import logging_error


@contextmanager
def handle_error(*exceptions, code=1):
    """Catch given `exceptions` and print there message to `stderr`. Exit
    system with given `code`.

    Args:
        exeception(iterable): of exception, which are handle by this context
        code(int): returned error-code
    Raises:
        SystemExitExecetion if given `exceptions` is raised while executing
        contextmanager.
    """
    try:
        yield
    except exceptions as error:
        logging_error(error)
        exit(code)
