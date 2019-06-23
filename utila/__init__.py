#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

# Public API:
# Classificator
from utila.classificator import determine_cluster
from utila.classificator import same_area_cluster
from utila.classificator import three_side_equal_cluster
# Cmdline
from utila.cmdline import INVALID_COMMAND
from utila.cmdline import Command
from utila.cmdline import Flag
from utila.cmdline import Parameter
from utila.cmdline import RequiredCommand
from utila.cmdline import parse
from utila.cmdline import sources
# Time
from utila.datetime import current
from utila.datetime import timedate
from utila.datetime import today
# Error
from utila.error import CANCELLED_BY_USER
from utila.error import handle_error
from utila.error import saveme
# Feature
from utila.feature import File
from utila.feature import Input
from utila.feature import Pattern
from utila.feature import ResultFile
from utila.feature import Value
from utila.feature import create_step
from utila.feature import featurepack
# File
from utila.file import assert_file
from utila.file import assert_html
from utila.file import assert_json
from utila.file import assert_yaml
from utila.file import copy_content
from utila.file import file_append
from utila.file import file_create
from utila.file import file_read
from utila.file import file_remove
from utila.file import file_replace
from utila.file import from_raw_or_path
from utila.file import tempfile
from utila.file import tempname
from utila.file import tmp
# likelihood
from utila.likelihood import uniform_result
# Logging
from utila.logging import flush
from utila.logging import logging
from utila.logging import logging_error
from utila.logging import logging_stacktrace
from utila.logging import print_runtime
from utila.logging import profile
# Tests
from utila.test import assert_run
from utila.test import assert_run_fail
from utila.test import clean_install
from utila.test import install_and_run
from utila.test import returncode
from utila.test import run
from utila.test import run_command
from utila.test import skip_nonvirtual
# Utils
from utila.utils import FAILURE
from utila.utils import INF
from utila.utils import NEWLINE
from utila.utils import SUCCESS
from utila.utils import UTF8
from utila.utils import fix_encoding
from utila.utils import forward_slash

__version__ = '0.7.1'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGENAME = 'utila'
