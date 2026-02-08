# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import time

import pytest
import utilatest

import utilo
import utilo.logger


def test_skipcollector():
    to_skip = [0, 5, 10]
    skipped = []

    with utilo.SkipCollector(pages=to_skip) as collector:
        for item in range(15):
            if not collector.skip(item):
                skipped.append(item)

    assert skipped == to_skip, str(skipped)


def test_skipcollector_none():
    with utilo.SkipCollector() as collector:
        assert not collector.skip(10)
        assert not collector.skip(20)


def test_skipcollector_single_int():
    """Skip all other pages than zero."""
    single_int = 0
    with utilo.SkipCollector(pages=single_int) as collector:
        assert not collector.skip(0)
        assert collector.skip(1)


def test_skipcollector_zero_tuple():
    """Skip all other pages than zero."""
    zero_tuple = (0,)
    with utilo.SkipCollector(pages=zero_tuple) as collector:
        assert not collector.skip(0)
        assert collector.skip(1)


@pytest.mark.parametrize('message', ['', 'setup'])
def test_profile(capsys, message):
    """Test that profiler print the `message` in combination of runtime"""
    with utilo.level_tmp(utilo.Level.INFO):
        with utilo.profile(message):
            pass
    stdout = utilatest.stdout(capsys)
    assert message in stdout, str(stdout)


def test_profile_with_exception(capsys):
    """Catch error while running profiling"""
    with pytest.raises(ValueError):
        with utilo.level_tmp(utilo.Level.INFO):
            with utilo.profile():
                raise ValueError('some problems in invocation')
    stdout = utilatest.stdout(capsys)
    assert 'runtime' in stdout, str(stdout)


def test_profiler_decorator(capsys):

    @utilo.profile('decorated profiler')
    def runtime():
        time.sleep(0.1)

    with utilo.level_tmp(utilo.Level.INFO):
        runtime()
    stdout = utilatest.stdout(capsys)
    assert 'decorated profiler' in stdout, str(stdout)


def test_print_env(capsys):
    with utilo.level_tmp(utilo.Level.INFO):
        utilo.print_env()
    stdout = utilatest.stdout(capsys)
    assert len(stdout) > 500, str(stdout)


def test_format_completed():
    completed = utilatest.run('pingosuperdumpa --help', expect=None)
    formatted = utilo.format_completed(completed)
    assert len(formatted) > 150, str(formatted)
    assert 'returncode: 1' in formatted, str(formatted)


@utilo.log_args
def add(x, y, z):  # pylint:disable=C0103
    return x + y + z


@pytest.mark.parametrize('level, expected_log', [
    pytest.param(
        utilo.Level.LOGGING,
        [''],
        id='no_logging',
    ),
    pytest.param(
        utilo.Level.INFO,
        ['x', 'y', 'y', '1', '2', '3'],
        id='logging info',
    ),
    pytest.param(
        utilo.Level.CALLS,
        ['x', 'y', 'z', '1', '2', '3'],
        id='logging calls',
    ),
])
def test_log_args(level, expected_log, capsys):
    with utilo.level_tmp(level):
        add(1, 2, 3)
    stdout = utilatest.stdout(capsys)
    for item in expected_log:
        assert item in stdout, stdout
    # ensure that no_logging does not log anything
    assert len(''.join(expected_log)) <= len(stdout.strip())


def test_log_args_loglevel_to_low(capsys):
    """Set `LEVEL` to `LOGGING` to avoid any output"""
    with utilo.level_tmp(utilo.Level.LOGGING):
        add(1, 2, 3)
    stdout = utilatest.stdout(capsys)
    assert not stdout, str(stdout)


def test_level_tmp():
    start = utilo.level_current()
    with utilo.level_tmp(utilo.Level.ERROR):
        setme = utilo.Level.DEBUG
        before = utilo.level_current()
        with utilo.level_tmp(setme):
            now = utilo.level_current()
        after = utilo.level_current()
    assert setme != before, f'{setme} must differ from default level {before}'
    assert before != now, 'context manager has no effect'
    assert after == before, 'the level was not set back to default'
    assert utilo.level_current() == start


def test_level_setup():
    utilo.level_setup(utilo.LEVEL_DEFAULT)
    start = utilo.level_current()
    assert utilo.level_current() == utilo.LEVEL_DEFAULT
    with utilo.level_tmp(utilo.Level.ERROR):
        setme = utilo.Level.DEBUG
        before = utilo.level_current()
        assert setme != before, f'{setme} must differ from default level {before}'
        utilo.level_setup(setme)
        after = utilo.level_current()
        assert after == setme, 'could not update log level'
    assert utilo.level_current() == start


def test_outfile(td):
    logger = os.path.join(td.tmpdir, 'logging.txt')
    with utilo.outfile_tmp(logger):
        utilo.log('First Line')
        utilo.log('Second Line')
        utilo.error('Third Line')
    # ensure to reset OUTFILE
    assert utilo.outfile() is None
    written = utilo.file_read(logger)
    expected = 'First Line\nSecond Line\n[ERROR] Third Line\n'
    assert written == expected


def test_outfile_delete_double(td):
    logger = os.path.join(td.tmpdir, 'logging.txt')
    with utilo.outfile_tmp(logger):
        utilo.outfile_setup(None)
        utilo.outfile_setup(None)


def test_multi_string(capsys):
    utilo.log('helm', 'schelm', end='')
    assert utilatest.stdout(capsys) == 'helm schelm'


def test_log_return_invalid_selection(capsys):

    @utilo.log_return
    def method_name(_):  # pylint:disable=W0613
        return 10

    with utilo.level_tmp(utilo.Level.DEBUG):
        method_name([10, 11])
    stdout = utilatest.stdout(capsys)
    assert 'selected index: 0' in stdout

    with utilo.level_tmp(utilo.Level.ERROR):
        method_name((1, 2, 3, 4))

    stderr = utilatest.stderr(capsys)
    assert '[ERROR] method_name select 10 is not possible' in stderr
