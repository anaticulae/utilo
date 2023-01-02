# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utila


def scramble(text: str, failure: int = 1, seed: float = 0.5) -> str:
    """\
    >>> scramble('Helmut')
    'Hulmet'
    >>> scramble('MAXIMUS HELMUTUS BONUS', failure=2)
    'MAUIMUB HELMXTUS SONUS'
    """
    changes = utila.choose_random(
        utila.rlist(len(text)),
        count=failure * 2,
        seed=seed,
    )
    for first, second in zip(changes[::2], changes[1::2]):
        # TODO: THERE MUST BE A BETTER WAY
        buf = text[first]
        text = text[0:first] + text[second] + text[first + 1:]
        text = text[0:second] + buf + text[second + 1:]
    return text


def ghost_replace(
    text: str,
    pattern: str,
    replacement='*',
    count: int = 1,
) -> str:
    """\
    >>> ghost_replace('Hier spricht Helm', 'prich')
    'Hier s*****t Helm'
    >>> ghost_replace('Helm Helm Helm', 'elm', count=1)
    'H*** Helm Helm'
    >>> ghost_replace('ABCDEFG', ('A', 'D', 'F'))
    '*BC*E*G'
    """
    if not isinstance(pattern, str):
        for patt in pattern:
            text = ghost_replace(
                text,
                pattern=patt,
                replacement=replacement,
                count=1,
            )
        return text
    new = replacement * len(pattern)
    text = text.replace(pattern, new, count)
    return text
