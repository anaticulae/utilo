#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

import os

# Public API:
# Classificator
from utila.classifier import common_items
from utila.classifier import determine_cluster
from utila.classifier import same_area_cluster
from utila.classifier import three_side_equal_cluster
# cli
from utila.cli import INVALID_COMMAND
from utila.cli import PAGES_FLAG
from utila.cli import Command
from utila.cli import Flag
from utila.cli import Number
from utila.cli import Parameter
from utila.cli import RequiredCommand
from utila.cli import is_userflag
from utila.cli import parse
from utila.cli import sources
from utila.cli import userflag_to_arg
# collection
from utila.collection import make_unique
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
from utila.feature import InterfaceMismatch
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
from utila.file import file_compare
from utila.file import file_copy
from utila.file import file_create
from utila.file import file_islocked
from utila.file import file_lock
from utila.file import file_read
from utila.file import file_read_binary
from utila.file import file_remove
from utila.file import file_replace
from utila.file import file_unlock
from utila.file import from_raw_or_path
from utila.file import isfilepath
from utila.file import make_absolute
from utila.file import make_package
from utila.file import make_relative
from utila.file import make_single
from utila.file import tmp
from utila.file import tmpfile
from utila.file import tmpname
from utila.file import yaml
# likelihood
from utila.likelihood import maxi
from utila.likelihood import mini
from utila.likelihood import uniform_result
# Logging
from utila.logger import LEVEL_DEFAULT
from utila.logger import Level
from utila.logger import SkipCollector
from utila.logger import call
from utila.logger import debug
from utila.logger import error
from utila.logger import format_completed
from utila.logger import info
from utila.logger import level_current
from utila.logger import level_setup
from utila.logger import level_temp
from utila.logger import log
from utila.logger import log_args
from utila.logger import log_stacktrace
from utila.logger import print_env
from utila.logger import print_runtime
from utila.logger import profile
# math
# from utila.math import Number TODO: ACTIVATE LATER
from utila.math import Numbers
from utila.math import isascending
from utila.math import modes
from utila.math import numbers
from utila.math import roundme
# pages
from utila.pages import parse_pages
from utila.pages import select_page
from utila.pages import should_skip
# process
from utila.process import run_parallel
# regex
from utila.regex import extract_match
# string
from utila.string import fix_encoding
from utila.string import forward_slash
# Tests
from utila.test import FASTRUN
from utila.test import LONGRUN
from utila.test import NIGHTLY
from utila.test import VIRTUAL
from utila.test import assert_failure
from utila.test import assert_run
from utila.test import assert_run_fail
from utila.test import assert_success
from utila.test import clean_install
from utila.test import increased_filecount
from utila.test import install_and_run
from utila.test import log_raw
from utila.test import returncode
from utila.test import run
from utila.test import run_command
from utila.test import single_execution
from utila.test import skip_longrun
from utila.test import skip_nightly
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
from utila.utils import chdir
from utila.utils import flatten
from utila.utils import nothing
from utila.utils import select

__version__ = '1.12.1'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGENAME = 'utila'
