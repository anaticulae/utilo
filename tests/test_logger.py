# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
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
