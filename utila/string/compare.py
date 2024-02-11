# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import difflib

import utila


def similar(expected: str, current: str, maxdiff=0.6) -> bool:
    """\
    >>> similar('Abbildungsverzeichnis', 'ab_ildungsverzeichnis')
    True
    >>> similar('Helm', 'Konrad')
    False
    >>> similar(['Abbildungsverzeichnis', 'Abbildungen'], 'Abbildung', maxdiff=0.1)
    True
    >>> similar({'WWW', 'HTTP', 'SSH'}, 'http')
    True
    >>> similar({'WWW', 'HTTP', 'SSH'}, 'AAA')
    False
    """
    # TODO: SWITCH EXPECTED AND CURRENT PARAMETER AND INCREASE MAJOR VERSION
    if not isinstance(expected, utila.ITERABLE):
        expected = [expected]
    expected = utila.strip(*expected)
    expected = utila.lower(*expected)
    expected = utila.nowhitespace(*expected)
    if isinstance(current, utila.ITERABLE):
        sim = any(
            similar(
                expected=expected,
                current=item,
                maxdiff=maxdiff,
            ) for item in current)
        if sim:
            return True
        return False
    current = current.strip().replace(' ', '').lower()
    matched = difflib.get_close_matches(
        word=current,
        possibilities=expected,
        n=1,
        cutoff=maxdiff,
    )
    if matched:
        return True
    return False


def verysimilar(current: str, expected: str) -> bool:
    """\
    >>> verysimilar('Hem', 'Helm')
    True
    >>> verysimilar('HemABC', 'HelmABC')
    True
    >>> verysimilar('A B S T R A C T', {'zusammenfassung', 'kurzfassung', 'abstract'})
    True
    >>> verysimilar(['current'], 'noe')
    False
    """
    if isinstance(current, str):
        current = [current]
    current = utila.nowhitespace(*current)
    if isinstance(expected, str):
        expected = [expected]
    maxdiff = 0.9
    if min(len(item) for item in expected) <= 4:
        maxdiff = 0.8
    if similar(current=current, expected=expected, maxdiff=maxdiff):
        return True
    return False
