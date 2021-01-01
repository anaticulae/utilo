# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import os
import time

import pytest
import utilatest

import utila
import utila.logger


def test_logger_skipcollector():
    to_skip = [0, 5, 10]
    skipped = []

    with utila.SkipCollector(pages=to_skip) as collector:
        for item in range(15):
            if not collector.skip(item):
                skipped.append(item)

    assert skipped == to_skip, str(skipped)


def test_logger_skipcollector_none():
    with utila.SkipCollector() as collector:
        assert collector.skip(10) is False
        assert collector.skip(20) is False


def test_logger_skipcollector_single_int():
    """Skip all other pages than zero."""
    single_int = 0
    with utila.SkipCollector(pages=single_int) as collector:
        assert collector.skip(0) is False
        assert collector.skip(1) is True


def test_logger_skipcollector_zero_tuple():
    """Skip all other pages than zero."""
    zero_tuple = (0,)
    with utila.SkipCollector(pages=zero_tuple) as collector:
        assert collector.skip(0) is False
        assert collector.skip(1) is True


@pytest.mark.parametrize('message', ['', 'setup'])
def test_logger_profile(capsys, message):
    """Test that profiler print the `message` in combination of runtime"""
    with utila.level_temp(utila.Level.INFORMATION):
        with utila.profile(message):
            pass
    stdout = capsys.readouterr().out
    assert message in stdout, str(stdout)


def test_logger_profile_with_exception(capsys):
    """Catch error while running profling"""
    with pytest.raises(ValueError):
        with utila.level_temp(utila.Level.INFORMATION):
            with utila.profile():
                raise ValueError('some problems in invocation')
    stdout = capsys.readouterr().out
    assert 'runtime' in stdout, str(stdout)


def test_profiler_decorator(capsys):

    @utila.profile('decorated profiler')
    def runtime():
        time.sleep(0.1)

    with utila.level_temp(utila.Level.INFORMATION):
        runtime()

    stdout = capsys.readouterr().out
    assert 'decorated profiler' in stdout, str(stdout)


def test_logger_print_env(capsys, monkeypatch):
    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'LEVEL', utila.Level.INFORMATION)
        utila.print_env()
    stdout = capsys.readouterr().out
    assert len(stdout) > 500, str(stdout)


def test_logger_format_completed():
    completed = utilatest.run('pingosuperdumpa --help', expect=None)
    formatted = utila.format_completed(completed)
    assert len(formatted) > 150, str(formatted)
    assert 'returncode: 1' in formatted, str(formatted)


@utila.log_args
def add(x, y, z):  # pylint:disable=C0103
    return x + y + z


@pytest.mark.parametrize('level, expected_log', [
    pytest.param(
        utila.Level.LOGGING,
        [''],
        id='no_logging',
    ),
    pytest.param(
        utila.Level.INFORMATION,
        ['x', 'y', 'y', '1', '2', '3'],
        id='logging info',
    ),
    pytest.param(
        utila.Level.CALLS,
        ['x', 'y', 'z', '1', '2', '3'],
        id='logging calls',
    ),
])
def test_logger_log_args(level, expected_log, capsys, monkeypatch):
    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'LEVEL', level)
        add(1, 2, 3)

    captured = capsys.readouterr().out

    for item in expected_log:
        assert item in captured, captured

    # ensure that no_logging does not log anything
    assert len(''.join(expected_log)) <= len(captured.strip())


def test_logger_log_args_loglevel_to_low(capsys, monkeypatch):
    """Set `LEVEL` to `LOGGING` to avoid any output"""
    with monkeypatch.context() as context:
        level = utila.Level.LOGGING
        context.setattr(utila.logger, 'LEVEL', level)
        add(1, 2, 3)

    captured = capsys.readouterr().out.strip()
    assert not captured, str(captured)


def test_logger_level_temp(monkeypatch):
    utila.level_setup(utila.LEVEL_DEFAULT)  # TODO: REMOVE LATER
    assert utila.level_current() == utila.LEVEL_DEFAULT
    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'LEVEL', utila.Level.ERROR)

        setme = utila.Level.DEBUG
        before = utila.level_current()
        with utila.level_temp(setme):
            now = utila.level_current()
        after = utila.level_current()

    assert setme != before, f'{setme} must differ from default level {before}'
    assert before != now, 'context manager has no effect'
    assert after == before, 'the level was not set back to default'
    assert utila.level_current() == utila.LEVEL_DEFAULT


def test_logger_level_setup(monkeypatch):
    utila.level_setup(utila.LEVEL_DEFAULT)  # TODO: REMOVE LATER
    assert utila.level_current() == utila.LEVEL_DEFAULT
    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'LEVEL', utila.Level.ERROR)

        setme = utila.Level.DEBUG
        before = utila.level_current()
        assert setme != before, f'{setme} must differ from default level {before}'

        utila.level_setup(setme)
        after = utila.level_current()
        assert after == setme, 'could not update log level'
    assert utila.level_current() == utila.LEVEL_DEFAULT


def test_logger_outfile(testdir, monkeypatch):
    logger = os.path.join(testdir.tmpdir, 'logging.txt')

    with monkeypatch.context() as context:
        context.setattr(utila.logger, 'OUTFILE', logger)

        utila.log('First Line')
        utila.log('Second Line')
        utila.error('Third Line')

    # ensure to reset OUTFILE
    assert utila.logger.OUTFILE is None

    written = utila.file_read(logger)
    expected = 'First Line\nSecond Line\n[ERROR] Third Line\n'

    assert written == expected
