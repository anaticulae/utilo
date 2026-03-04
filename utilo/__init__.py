#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

__version__ = '2.106.2'

import os

# Public API:
# to do
from utilo.__todo__ import docu
from utilo.__todo__ import refactor
from utilo.__todo__ import todo
# alpha
from utilo.alpha import alphabetically
from utilo.alpha import replace
from utilo.alpha import sort
# project
from utilo.baw import baw_config
from utilo.baw import baw_desc
from utilo.baw import baw_name
from utilo.baw import baw_root
# cacher
from utilo.cacher import cache_clear
from utilo.cacher import cache_disable
from utilo.cacher import cache_enable
from utilo.cacher import cacheme
# classes
from utilo.classes import collect_classes
from utilo.classes import name_classes
# classifier
from utilo.classifier.base import Cluster
from utilo.classifier.base import Clusters
from utilo.classifier.base import clusterme
from utilo.classifier.base import determine_cluster
from utilo.classifier.public import common_items
from utilo.classifier.public import intersecting_line_cluster
from utilo.classifier.public import max_distance
from utilo.classifier.public import rect_intersecting_cluster
from utilo.classifier.public import same_area_cluster
from utilo.classifier.public import same_line_cluster
from utilo.classifier.public import three_side_equal_cluster
from utilo.classifier.strategy import MatchStrategy
# cli
from utilo.cli import INVALID_COMMAND
from utilo.cli import PAGES_FLAG
from utilo.cli import Command
from utilo.cli import Commands
from utilo.cli import Flag
from utilo.cli import FlagCounted
from utilo.cli import NumberedParameter
from utilo.cli import Parameter
from utilo.cli import ParameterAppended
from utilo.cli import ParserConfiguration
from utilo.cli import RequiredCommand
from utilo.cli import create_parser
from utilo.cli import isuserflag
from utilo.cli import pages_fromargs
from utilo.cli import parse
from utilo.cli import sources
from utilo.cli import userflag_to_arg
# collection
from utilo.collection import Buckets
from utilo.collection import LowerCasedSet
from utilo.collection import Single
from utilo.collection import UpperCasedSet
from utilo.collection import choose_random
from utilo.collection import chunks
from utilo.collection import counts
from utilo.collection import dict_reverse
from utilo.collection import dicts_united
from utilo.collection import first_one
from utilo.collection import minimal
from utilo.collection import partition
from utilo.collection import sort_both
from utilo.collection import split_shuffle
from utilo.collection import splitby_count
from utilo.collection import starmap
from utilo.collection import unique
# color
from utilo.color import int2rgb
from utilo.color import rgb2int
# config
from utilo.config import dump_config
from utilo.config import load_config
# convert
from utilo.convert import int_ornone
from utilo.convert import parse_float
from utilo.convert import parse_floats
from utilo.convert import parse_int
from utilo.convert import parse_ints
from utilo.convert import parse_state
from utilo.convert import simplify
from utilo.convert import str2bool
from utilo.convert import str2float
from utilo.convert import str2int
# Time
from utilo.datetime import current
from utilo.datetime import filetime
from utilo.datetime import now
from utilo.datetime import timedate
from utilo.datetime import today
# decorator
from utilo.decorator import EMPTY
from utilo.decorator import decorateme
from utilo.decorator import decorators
from utilo.decorator import empty_replace
from utilo.decorator import isdecorated
# Error
from utilo.error import CANCELLED_BY_USER
from utilo.error import handle_error
from utilo.error import saveme
# cache
from utilo.feature.cache import datapackage
# Feature
from utilo.feature.pack import FeaturePackConfig
from utilo.feature.pack import featurepack
# path
from utilo.feature.path import connector as pathconnector
# processor
from utilo.feature.processor import NO_RESULT
from utilo.feature.processor import InterfaceMismatch
from utilo.feature.processor import Pipeline
from utilo.feature.processor import select_executor
# user input
from utilo.feature.userinput import Bool
from utilo.feature.userinput import Directory
from utilo.feature.userinput import File
from utilo.feature.userinput import Input
from utilo.feature.userinput import Pattern
from utilo.feature.userinput import ResultFile
from utilo.feature.userinput import Value
from utilo.feature.userinput import WorkPlanStep
from utilo.feature.userinput import create_step
from utilo.feature.workplan import parallelize as parallelize_workplan
# File
from utilo.file import assert_file
from utilo.file import assert_html
from utilo.file import assert_json
from utilo.file import assert_yaml
from utilo.file import file_append
from utilo.file import file_compare
from utilo.file import file_copy
from utilo.file import file_count
from utilo.file import file_create
from utilo.file import file_create_binary
from utilo.file import file_create_tmp
from utilo.file import file_ext
from utilo.file import file_islocked
from utilo.file import file_list
from utilo.file import file_lock
from utilo.file import file_name
from utilo.file import file_read
from utilo.file import file_read_binary
from utilo.file import file_remove
from utilo.file import file_replace
from utilo.file import file_replace_binary
from utilo.file import file_unlock
from utilo.file import files_sort
from utilo.file import make_absolute
from utilo.file import make_package
from utilo.file import make_relative
from utilo.file import make_single
from utilo.file import make_tmpdir
from utilo.file import tmp
from utilo.file import tmpdir
from utilo.file import tmpfile
from utilo.file import tmpname
from utilo.file import yaml
# file:action
from utilo.file.action import copy_content
from utilo.file.action import file_read_lines
# directory
from utilo.file.directory import directory_list
from utilo.file.directory import directory_lock
from utilo.file.directory import directory_unlock
from utilo.file.directory import tree_remove
# hashed
from utilo.file.hashed import directory_hash
from utilo.file.hashed import file_hash
# file:info
from utilo.file.info import file_age
from utilo.file.info import file_age_update
from utilo.file.info import file_line_length
from utilo.file.info import file_size
from utilo.file.info import isfilepath
from utilo.file.info import path_current
from utilo.file.info import path_parent
# loader
from utilo.file.loader import LazyFile
from utilo.file.loader import from_raw_or_path
from utilo.file.loader import yaml_dump
from utilo.file.loader import yaml_load
# utile
from utilo.file.utils import exists
from utilo.file.utils import exists_assert
from utilo.file.utils import join
from utilo.file.utils import pathexists
# group
from utilo.group import groupby_ascending
from utilo.group import groupby_diff
from utilo.group import groupby_empty
from utilo.group import groupby_neighbors
from utilo.group import groupby_none
from utilo.group import groupby_x
from utilo.group import longest
from utilo.group import shortest
from utilo.group import xsome
# hash
from utilo.hash import freehash
from utilo.hash import secure_hash
# likelihood
from utilo.likelihood import maxi
from utilo.likelihood import mini
from utilo.likelihood import select_maxi
from utilo.likelihood import uniform_result
# Logging
from utilo.logger import LEVEL_DEFAULT
from utilo.logger import Level
from utilo.logger import SkipCollector
from utilo.logger import call
from utilo.logger import capture_stderr
from utilo.logger import capture_stdout
from utilo.logger import debug
from utilo.logger import debug_enable
from utilo.logger import error
from utilo.logger import format_completed
from utilo.logger import info
from utilo.logger import level_current
from utilo.logger import level_setup
from utilo.logger import level_tmp
from utilo.logger import log
from utilo.logger import log_args
from utilo.logger import log_raw
from utilo.logger import log_return
from utilo.logger import outfile
from utilo.logger import outfile_setup
from utilo.logger import outfile_tmp
from utilo.logger import print_banner
from utilo.logger import print_env
from utilo.logger import print_runtime
from utilo.logger import print_stacktrace
from utilo.logger import profile
from utilo.logger import verbose
from utilo.logger import warning
# math
from utilo.math import Strategy
from utilo.math import diff_mode
from utilo.math import diffs
from utilo.math import gradient
from utilo.math import isascending
from utilo.math import lookup
from utilo.math import mode
from utilo.math import modes
from utilo.math import roundme
from utilo.math import roundshe
from utilo.math.const import isequal
from utilo.math.const import isinf
from utilo.math.const import isinside
from utilo.math.const import isone
from utilo.math.const import isoutside
from utilo.math.const import iszero
# math:distance
from utilo.math.distance import manhattan
from utilo.math.distance import norm
from utilo.math.distance import norms
# math:func
from utilo.math.func import ranged_exp
# math:line
from utilo.math.line import IndenticalLineError
from utilo.math.line import equal_lines
from utilo.math.line import intersecting_ending
from utilo.math.line import intersecting_lines
from utilo.math.line import isdot
from utilo.math.line import length
from utilo.math.line import line_raising
from utilo.math.line import merge_lines
from utilo.math.line import round_line
from utilo.math.line import unique_lines
# math:near
from utilo.math.near import near
from utilo.math.near import near_dims
from utilo.math.near import nears
from utilo.math.near import pnear
from utilo.math.near import verynear
# math:number
from utilo.math.number import Floats
from utilo.math.number import Ints
from utilo.math.number import Number
from utilo.math.number import Numbers
from utilo.math.number import between
from utilo.math.number import iseven
from utilo.math.number import isodd
from utilo.math.number import least
from utilo.math.number import limit
from utilo.math.number import maxs
from utilo.math.number import mins
from utilo.math.number import numbers
from utilo.math.number import numbers_random
from utilo.math.number import threshold
# rectangle
from utilo.math.rectangle import Rectangle
from utilo.math.rectangle import RectangleCheck
from utilo.math.rectangle import Rectangles
from utilo.math.rectangle import dot_in_rectangle
from utilo.math.rectangle import rect_border
from utilo.math.rectangle import rect_border_points
from utilo.math.rectangle import rect_center
from utilo.math.rectangle import rect_ensure_bounding
from utilo.math.rectangle import rect_height
from utilo.math.rectangle import rect_inside
from utilo.math.rectangle import rect_intersecting
from utilo.math.rectangle import rect_max
from utilo.math.rectangle import rect_merge
from utilo.math.rectangle import rect_overlapping
from utilo.math.rectangle import rect_roundsmall
from utilo.math.rectangle import rect_scale
from utilo.math.rectangle import rect_size
from utilo.math.rectangle import rect_width
from utilo.math.rectangle import rectangles_intersecting
from utilo.math.rectangle import sort_leftright_topdown
from utilo.math.rectangle import sort_leftright_topdown_upper
# roman
from utilo.math.roman import arabic
from utilo.math.roman import isarabic
from utilo.math.roman import isroman
from utilo.math.roman import pagenumber
from utilo.math.roman import pagenumber_minus
from utilo.math.roman import pagenumber_plus
from utilo.math.roman import roman
# optimizer
from utilo.optimizer import zip_optimizer
# pages
from utilo.pages import PageGenerator
from utilo.pages import SelectPage
from utilo.pages import pages_inside
from utilo.pages import parse_pages
from utilo.pages import select_content
from utilo.pages import select_page
from utilo.pages import select_pages
from utilo.pages import should_skip
from utilo.pages import simplify_pages
from utilo.pages import sync_pages
# process
from utilo.process import GeorgFork
from utilo.process import Timeout
from utilo.process import Waiter
from utilo.process import assert_failure
from utilo.process import assert_success
from utilo.process import exitx
from utilo.process import fork
from utilo.process import killpid
from utilo.process import process_ids
from utilo.process import returnvalue as returncode
from utilo.process import run
from utilo.process import run_parallel
# quick
from utilo.quick import install
from utilo.quick import version
# regex
from utilo.regex import NOCASE_VERBOSE
from utilo.regex import compiles
from utilo.regex import extract_match
from utilo.regex import finditer
from utilo.regex import match
from utilo.regex import search
# secret
from utilo.secret import decrypt
from utilo.secret import encrypt
# space
from utilo.space import inch
from utilo.space import millimeter
from utilo.space import millimeters
from utilo.space import point
from utilo.space import points
# string
from utilo.string import assert_bin
from utilo.string import binhash
from utilo.string import char_rate
from utilo.string import dict_dump
from utilo.string import final_newline
from utilo.string import findindex
from utilo.string import findindexs
from utilo.string import fix_encoding
from utilo.string import forward_slash
from utilo.string import inside
from utilo.string import issinglechar
from utilo.string import istemplate_replaced
from utilo.string import lower
from utilo.string import normalize_text
from utilo.string import normalize_whitespaces
from utilo.string import nowhitespace
from utilo.string import rreplace
from utilo.string import shrink
from utilo.string import simple
from utilo.string import simplify_chars
from utilo.string import splitdouble
from utilo.string import splititems
from utilo.string import splitlines
from utilo.string import starts_with
from utilo.string import starts_withint
from utilo.string import strip
from utilo.string.compare import similar
from utilo.string.compare import verysimilar
from utilo.string.display import diffview
from utilo.string.modify import ghost_replace
from utilo.string.modify import scramble
from utilo.string.table import TablePrinter
from utilo.string.table import table_smallest
# tuples
from utilo.tuples import crange
from utilo.tuples import cstart
from utilo.tuples import from_tuple
from utilo.tuples import make_tuple
from utilo.tuples import parse_tuple
from utilo.tuples import ranges
from utilo.tuples import rlist
from utilo.tuples import rtuple
from utilo.tuples import tuple_mult
from utilo.tuples import tuple_plus
from utilo.tuples import update_tuple
# type-checker
from utilo.typechecker import Strings
from utilo.typechecker import annotations
from utilo.typechecker import asserts
from utilo.typechecker import asserts_types
from utilo.typechecker import attributes
from utilo.typechecker import checkdatatype
from utilo.typechecker import defaults
from utilo.typechecker import defaults_overwrite
from utilo.typechecker import equal_length
from utilo.typechecker import hasattribute
from utilo.typechecker import isfloat
from utilo.typechecker import isint
from utilo.typechecker import isnumber
from utilo.typechecker import isstrings
from utilo.typechecker import load_module
from utilo.typechecker import methods
from utilo.typechecker import pass_required
from utilo.typechecker import rename
# utile
from utilo.utils import ALL_PAGES
from utilo.utils import FAILURE
from utilo.utils import INF
from utilo.utils import ITERABLE
from utilo.utils import NEWLINE
from utilo.utils import NL
from utilo.utils import SUCCESS
from utilo.utils import TMP
from utilo.utils import U8
from utilo.utils import UTF8
from utilo.utils import Nothing
from utilo.utils import assert_unique
from utilo.utils import chdir
from utilo.utils import cwdget
from utilo.utils import driver
from utilo.utils import ensure_list
from utilo.utils import ensure_tuple
from utilo.utils import flat
from utilo.utils import flatten_content
from utilo.utils import hasprog
from utilo.utils import iflat
from utilo.utils import ifnone
from utilo.utils import index_max
from utilo.utils import isci
from utilo.utils import ismainthread
from utilo.utils import iswin
from utilo.utils import iterable
from utilo.utils import mainthread
from utilo.utils import minus
from utilo.utils import notempty
from utilo.utils import nothing
from utilo.utils import notnone
from utilo.utils import pagebox_hash
from utilo.utils import rate_rel
from utilo.utils import rate_sum
from utilo.utils import removekeys
from utilo.utils import sall_false
from utilo.utils import sall_none
from utilo.utils import sall_true
from utilo.utils import sattr
from utilo.utils import scall_or_me
from utilo.utils import selbstwirksamkeit
from utilo.utils import select_type
from utilo.utils import sfirst
from utilo.utils import ssecond
from utilo.utils import sthird
from utilo.utils import testing
from utilo.utils import unset_env
from utilo.utils import wait

# TODO: REMOVE LATER AND INCREASE MAJOR VERSION NUMBER
flatten = flat  # pylint:disable=C0103
iflatten = iflat  # pylint:disable=C0103
not_none = notnone  # pylint:disable=C0103
manhatten = manhattan  # pylint:disable=C0103
log_stacktrace = print_stacktrace  # pylint:disable=C0103
assert_type_list = asserts_types  # pylint:disable=C0103
islist = iterable  # pylint:disable=C0103
level_temp = level_tmp  # pylint:disable=C0103
yaml_from_raw_or_path = yaml_load  # pylint:disable=C0103
parse_numbers = parse_ints  # pylint:disable=C0103
intersecting_rectangle = rect_intersecting  # pylint:disable=C0103
intersecting_rectangle_cluster = rect_intersecting_cluster  # pylint:disable=C0103
rectangle_border = rect_border  # pylint:disable=C0103
rectangle_border_points = rect_border_points  # pylint:disable=C0103
rectangle_center = rect_center  # pylint:disable=C0103
rectangle_ensure_bounding = rect_ensure_bounding  # pylint:disable=C0103
rectangle_height = rect_height  # pylint:disable=C0103
rectangle_inside = rect_inside  # pylint:disable=C0103
rectangle_intersecting = rect_intersecting  # pylint:disable=C0103
rectangle_max = rect_max  # pylint:disable=C0103
rectangle_merge = rect_merge  # pylint:disable=C0103
rectangle_overlapping = rect_overlapping  # pylint:disable=C0103
rectangle_roundsmall = rect_roundsmall  # pylint:disable=C0103
rectangle_scale = rect_scale  # pylint:disable=C0103
rectangle_size = rect_size  # pylint:disable=C0103
rectangle_width = rect_width  # pylint:disable=C0103
ranged_list = rlist  # pylint:disable=C0103
ranged_tuple = rtuple  # pylint:disable=C0103
make_unique = unique

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE = 'utilo'
