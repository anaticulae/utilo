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
from utila.cli import INVALID_COMMAND
from utila.cli import Command
from utila.cli import Flag
from utila.cli import Parameter
from utila.cli import RequiredCommand
from utila.cli import parse
from utila.cli import sources
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
from utila.feature import parallelize_workplan
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
from utila.file import tmp
from utila.file import tmpfile
from utila.file import tmpname
# likelihood
from utila.likelihood import uniform_result
from utila.likelihood import uniform_result_with_items
# Logging
from utila.logger import Level
from utila.logger import SkipCollector
from utila.logger import call
from utila.logger import debug
from utila.logger import error
from utila.logger import info
from utila.logger import level_setup
from utila.logger import log
from utila.logger import log_stacktrace
from utila.logger import print_runtime
from utila.logger import profile
# pages
from utila.pages import pages
from utila.pages import should_skip
# string
from utila.string import fix_encoding
from utila.string import forward_slash
# Tests
from utila.test import FASTRUN
from utila.test import LONGRUN
from utila.test import VIRTUAL
from utila.test import assert_run
from utila.test import assert_run_fail
from utila.test import clean_install
from utila.test import install_and_run
from utila.test import returncode
from utila.test import run
from utila.test import run_command
from utila.test import skip_longrun
from utila.test import skip_nonvirtual
from utila.test import skip_virtual
# Typerchecker
from utila.typechecker import checkdatatype
# Utils
from utila.utils import FAILURE
from utila.utils import INF
from utila.utils import NEWLINE
from utila.utils import SUCCESS
from utila.utils import UTF8
from utila.utils import flatten
from utila.utils import roundme

__version__ = '1.2.5'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGENAME = 'utila'
