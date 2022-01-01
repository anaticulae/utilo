# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2020-2022 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================
"""Alpha
=====

This module provides methods to work with german languages constructs.

Sort alphabetical
-----------------

>>> items = [(0, 'Helm'), (5, 'Schelm'), (3, 'Gelm')]
>>> sorted(items, key=lambda x: alphabetically(x[1]))
[(3, 'Gelm'), (0, 'Helm'), (5, 'Schelm')]

Nones are sorted to the end of the list.

>>> sorted([(0, None), (3, 'Gelm')], key=lambda x: alphabetically(x[1]))
[(3, 'Gelm'), (0, None)]

"""

import contextlib


def sort(*items):
    """Sort words included Greek letter alphabetically.

    >>> sort('Alpha', 'α', 'Gamma', 'beta')
    ['α', 'Alpha', 'beta', 'Gamma']
    >>> sort('Hulle', 'Hülle')
    ['Hülle', 'Hulle']
    """
    return sorted(items, key=alphabetically)


def replace(*items):
    """Convert to ASCII.

    >>> replace('α', 'χ', '²', 'Abc')
    ['a', 'c', '2', 'Abc']
    >>> replace('Hαχ²')
    'Hac2'
    >>> replace('χ')
    'c'
    """
    result = []
    for item in items:
        replaced = []
        for char in item:
            with contextlib.suppress(KeyError):
                char = MATCHED[char]
            replaced.append(char)
        result.append(''.join(replaced))
    if len(result) == 1:
        return result[0]
    return result


def alphabetically(item: str) -> str:
    if item is None:
        # sort at the end, use max value
        return chr(0x10ffff)
    return replace(item).lower()


TABLE = """\
α           a
β           b
γ           g
δ           d
ε           ep
ζ           z
η           et
θ           t
ι           i
κ           k
λ           l
μ           m
ν           n
ξ           x
π           pi
ρ           r
σ           s
τ           t
υ           up
φ           phi
χ           c
ψ           psi
ω           o
Γ           G
Δ           E
Θ           T
Λ           L
Ξ           X
Π           PI
Σ           SI
Υ           UP
Φ           PH
Ψ           PS
Ω           OM
⁰           0
¹           1
²           2
³           3
⁴           4
⁵           5
⁶           6
⁷           7
⁸           8
⁹           9
₀           0
₁           1
₂           2
₃           3
₄           4
₅           5
₆           6
₇           7
₈           8
₉           9
ä           ae
ö           oe
ü           ue
Ä           AE
Ö           OE
Ü           UE
ß           ss
"""
# TODO: REPLACE WITH SHARK OPERATOR, PYTHON 3.8
MATCHED = {
    item.split()[0]: item.split()[1] for item in TABLE.strip().splitlines()
}
