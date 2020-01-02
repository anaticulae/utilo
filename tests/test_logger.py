# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2020 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import pytest

import utila


def test_logger_skipcollector():
    to_skip = [0, 5, 10]
    skipped = []

    with utila.SkipCollector(pages=to_skip) as collector:
        for item in range(15):
            if not collector.skip(item):
                skipped.append(item)

    assert skipped == to_skip, str(skipped)


@pytest.mark.parametrize('message', ['', 'setup'])
def test_logger_profile(capsys, message):
    """Test that profiler print the `message` in combination of runtime"""
    with utila.profile(message):
        pass
    stdout = capsys.readouterr().out
    assert message in stdout, str(stdout)


def test_logger_profile_with_exception(capsys):
    """Catch error while running profling"""
    with pytest.raises(ValueError):
        with utila.profile():
            raise ValueError('some problems in invocation')

    stdout = capsys.readouterr().out
    assert 'Runtime' in stdout, str(stdout)


def test_logger_print_env(capsys, monkeypatch):
    with monkeypatch.context() as context:
        context.setattr('utila.logger.LEVEL', utila.Level.INFORMATION)
        utila.print_env()
    stdout = capsys.readouterr().out
    assert len(stdout) > 500, str(stdout)


def test_logger_format_completed():
    completed = utila.run('pingosuperdumpa --help')
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
        context.setattr('utila.logger.LEVEL', level)
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
        context.setattr('utila.logger.LEVEL', level)
        add(1, 2, 3)

    captured = capsys.readouterr().out.strip()
    assert not captured, str(captured)
