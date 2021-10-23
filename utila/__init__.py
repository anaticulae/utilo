#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

__version__ = '2.59.1'

import os

# Public API:
# to do
from utila.__todo__ import docu
from utila.__todo__ import refactor
from utila.__todo__ import todo
# alpha
from utila.alpha import alphabetically
from utila.alpha import replace
from utila.alpha import sort
# classes
from utila.classes import collect_classes
from utila.classes import name_classes
# classifier
from utila.classifier.base import Cluster
from utila.classifier.base import Clusters
from utila.classifier.base import clusterme
from utila.classifier.base import determine_cluster
from utila.classifier.public import common_items
from utila.classifier.public import intersecting_line_cluster
from utila.classifier.public import intersecting_rectangle_cluster
from utila.classifier.public import max_distance
from utila.classifier.public import same_area_cluster
from utila.classifier.public import same_line_cluster
from utila.classifier.public import three_side_equal_cluster
from utila.classifier.strategy import MatchStrategy
# cli
from utila.cli import INVALID_COMMAND
from utila.cli import PAGES_FLAG
from utila.cli import Command
from utila.cli import Commands
from utila.cli import Flag
from utila.cli import FlagCounted
from utila.cli import NumberedParameter
from utila.cli import Parameter
from utila.cli import ParameterAppended
from utila.cli import ParserConfiguration
from utila.cli import RequiredCommand
from utila.cli import create_parser
from utila.cli import isuserflag
from utila.cli import pages_fromargs
from utila.cli import parse
from utila.cli import sources
from utila.cli import userflag_to_arg
# collection
from utila.collection import Buckets
from utila.collection import LowerCasedSet
from utila.collection import Single
from utila.collection import UpperCasedSet
from utila.collection import choose_random
from utila.collection import chunks
from utila.collection import counts
from utila.collection import dict_reverse
from utila.collection import dicts_united
from utila.collection import first_one
from utila.collection import make_unique
from utila.collection import minimal
from utila.collection import partition
from utila.collection import split_shuffle
from utila.collection import starmap
# config
from utila.config import dump_config
from utila.config import load_config
# convert
from utila.convert import parse_floats
from utila.convert import parse_numbers
from utila.convert import simplify
from utila.convert import str2bool
from utila.convert import str2float
from utila.convert import str2int
# Time
from utila.datetime import current
from utila.datetime import filetime
from utila.datetime import now
from utila.datetime import timedate
from utila.datetime import today
# decorator
from utila.decorator import decorateme
from utila.decorator import decorators
from utila.decorator import isdecorated
# Error
from utila.error import CANCELLED_BY_USER
from utila.error import handle_error
from utila.error import saveme
# Feature
from utila.feature import FeaturePackConfig
from utila.feature import InterfaceMismatch
from utila.feature import featurepack
# cache
from utila.feature.cache import datapackage
# path
from utila.feature.path import connector as pathconnector
# processor
from utila.feature.processor import NO_RESULT
from utila.feature.processor import select_executor
# user input
from utila.feature.userinput import Bool
from utila.feature.userinput import Directory
from utila.feature.userinput import File
from utila.feature.userinput import Input
from utila.feature.userinput import Pattern
from utila.feature.userinput import ResultFile
from utila.feature.userinput import Value
from utila.feature.userinput import WorkPlanStep
from utila.feature.userinput import create_step
from utila.feature.workplan import parallelize as parallelize_workplan
# File
from utila.file import assert_file
from utila.file import assert_html
from utila.file import assert_json
from utila.file import assert_yaml
from utila.file import file_append
from utila.file import file_compare
from utila.file import file_copy
from utila.file import file_count
from utila.file import file_create
from utila.file import file_create_binary
from utila.file import file_create_tmp
from utila.file import file_ext
from utila.file import file_islocked
from utila.file import file_list
from utila.file import file_lock
from utila.file import file_name
from utila.file import file_read
from utila.file import file_read_binary
from utila.file import file_remove
from utila.file import file_replace
from utila.file import file_replace_binary
from utila.file import file_unlock
from utila.file import files_sort
from utila.file import make_absolute
from utila.file import make_package
from utila.file import make_relative
from utila.file import make_single
from utila.file import make_tmpdir
from utila.file import tmp
from utila.file import tmpdir
from utila.file import tmpfile
from utila.file import tmpname
from utila.file import yaml
# file:action
from utila.file.action import copy_content
from utila.file.action import file_read_lines
# directory
from utila.file.directory import directory_list
# hashed
from utila.file.hashed import directory_hash
from utila.file.hashed import file_hash
# file:info
from utila.file.info import file_age
from utila.file.info import file_age_update
from utila.file.info import file_line_length
from utila.file.info import file_size
from utila.file.info import isfilepath
from utila.file.info import path_current
from utila.file.info import path_parent
# loader
from utila.file.loader import LazyFile
from utila.file.loader import from_raw_or_path
from utila.file.loader import yaml_dump
from utila.file.loader import yaml_load
# utile
from utila.file.utils import exists
from utila.file.utils import exists_assert
from utila.file.utils import pathexists
# group
from utila.group import groupby_ascending
from utila.group import groupby_diff
from utila.group import groupby_empty
from utila.group import groupby_neighbors
from utila.group import groupby_none
from utila.group import groupby_x
from utila.group import longest
from utila.group import shortest
from utila.group import xsome
# hash
from utila.hash import freehash
from utila.hash import secure_hash
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
from utila.logger import level_tmp
from utila.logger import log
from utila.logger import log_args
from utila.logger import log_raw
from utila.logger import outfile
from utila.logger import print_banner
from utila.logger import print_env
from utila.logger import print_runtime
from utila.logger import print_stacktrace
from utila.logger import profile
# math
from utila.math import Strategy
from utila.math import diff_mode
from utila.math import diffs
from utila.math import isascending
from utila.math import lookup
from utila.math import mode
from utila.math import modes
from utila.math import roundme
from utila.math import roundshe
from utila.math.const import isequal
from utila.math.const import isinf
from utila.math.const import isinside
from utila.math.const import isone
from utila.math.const import isoutside
from utila.math.const import iszero
# math:distance
from utila.math.distance import manhattan
from utila.math.distance import norm
from utila.math.distance import norms
# math:func
from utila.math.func import ranged_exp
# math:line
from utila.math.line import IndenticalLineError
from utila.math.line import equal_lines
from utila.math.line import intersecting_ending
from utila.math.line import intersecting_lines
from utila.math.line import isdot
from utila.math.line import length
from utila.math.line import line_raising
from utila.math.line import merge_lines
from utila.math.line import round_line
from utila.math.line import unique_lines
# math:near
from utila.math.near import near
from utila.math.near import near_dims
from utila.math.near import nears
from utila.math.near import pnear
from utila.math.near import verynear
# math:number
from utila.math.number import Floats
from utila.math.number import Ints
from utila.math.number import Number
from utila.math.number import Numbers
from utila.math.number import between
from utila.math.number import least
from utila.math.number import limit
from utila.math.number import maxs
from utila.math.number import mins
from utila.math.number import numbers
from utila.math.number import numbers_random
from utila.math.number import threshold
# rectangle
from utila.math.rectangle import Rectangle
from utila.math.rectangle import RectangleCheck
from utila.math.rectangle import Rectangles
from utila.math.rectangle import dot_in_rectangle
from utila.math.rectangle import intersecting_rectangle
from utila.math.rectangle import rectangle_border
from utila.math.rectangle import rectangle_border_points
from utila.math.rectangle import rectangle_center
from utila.math.rectangle import rectangle_ensure_bounding
from utila.math.rectangle import rectangle_height
from utila.math.rectangle import rectangle_inside
from utila.math.rectangle import rectangle_max
from utila.math.rectangle import rectangle_merge
from utila.math.rectangle import rectangle_roundsmall
from utila.math.rectangle import rectangle_scale
from utila.math.rectangle import rectangle_size
from utila.math.rectangle import rectangle_width
from utila.math.rectangle import rectangles_intersecting
from utila.math.rectangle import sort_leftright_topdown
from utila.math.rectangle import sort_leftright_topdown_upper
# roman
from utila.math.roman import arabic
from utila.math.roman import isarabic
from utila.math.roman import isroman
from utila.math.roman import roman
# optimizer
from utila.optimizer import zip_optimizer
# pages
from utila.pages import parse_pages
from utila.pages import select_content
from utila.pages import select_page
from utila.pages import select_pages
from utila.pages import should_skip
from utila.pages import simplify_pages
from utila.pages import sync_pages
# process
from utila.process import GeorgFork
from utila.process import Timeout
from utila.process import Waiter
from utila.process import assert_failure
from utila.process import assert_success
from utila.process import fork
from utila.process import returnvalue as returncode
from utila.process import run
from utila.process import run_parallel
# regex
from utila.regex import NOCASE_VERBOSE
from utila.regex import compiles
from utila.regex import extract_match
from utila.regex import finditer
from utila.regex import match
from utila.regex import search
# secret
from utila.secret import decrypt
from utila.secret import encrypt
# space
from utila.space import inch
from utila.space import millimeter
from utila.space import millimeters
from utila.space import point
from utila.space import points
# string
from utila.string import assert_bin
from utila.string import binhash
from utila.string import char_rate
from utila.string import findindex
from utila.string import findindexs
from utila.string import fix_encoding
from utila.string import forward_slash
from utila.string import inside
from utila.string import istemplate_replaced
from utila.string import lower
from utila.string import normalize_text
from utila.string import normalize_whitespaces
from utila.string import rreplace
from utila.string import shrink
from utila.string import similar
from utila.string import simple
from utila.string import simplify_chars
from utila.string import splititems
from utila.string import splitlines
from utila.string import starts_with
from utila.string import starts_withint
from utila.string import strip
from utila.string import verysimilar
# tuples
from utila.tuples import from_tuple
from utila.tuples import make_tuple
from utila.tuples import parse_tuple
from utila.tuples import ranged_list
from utila.tuples import ranged_tuple
from utila.tuples import ranges
from utila.tuples import tuple_mult
from utila.tuples import tuple_plus
from utila.tuples import update_tuple
# type-checker
from utila.typechecker import Strings
from utila.typechecker import asserts
from utila.typechecker import asserts_types
from utila.typechecker import attributes
from utila.typechecker import checkdatatype
from utila.typechecker import equal_length
from utila.typechecker import hasattribute
from utila.typechecker import isfloat
from utila.typechecker import isint
from utila.typechecker import isnumber
from utila.typechecker import isstrings
from utila.typechecker import load_module
from utila.typechecker import pass_required
# utile
from utila.utils import ALL_PAGES
from utila.utils import FAILURE
from utila.utils import INF
from utila.utils import ITERABLE
from utila.utils import NEWLINE
from utila.utils import NL
from utila.utils import SUCCESS
from utila.utils import TMP
from utila.utils import U8
from utila.utils import UTF8
from utila.utils import chdir
from utila.utils import ensure_list
from utila.utils import ensure_tuple
from utila.utils import flatten
from utila.utils import flatten_content
from utila.utils import ifnone
from utila.utils import index_max
from utila.utils import iseven
from utila.utils import iterable
from utila.utils import minus
from utila.utils import notempty
from utila.utils import nothing
from utila.utils import notnone
from utila.utils import rate_rel
from utila.utils import rate_sum
from utila.utils import removekeys
from utila.utils import selbstwirksamkeit
from utila.utils import select_type
from utila.utils import unset_env

# TODO: REMOVE LATER AND INCREASE MAJOR VERSION NUMBER
not_none = notnone  # pylint:disable=C0103
manhatten = manhattan  # pylint:disable=C0103
log_stacktrace = print_stacktrace  # pylint:disable=C0103
assert_type_list = asserts_types  # pylint:disable=C0103
islist = iterable  # pylint:disable=C0103
level_temp = level_tmp
yaml_from_raw_or_path = yaml_load

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE = 'utila'
