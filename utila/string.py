# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2021 by Helmut Konrad Fahrendholz. All rights reserved.
# This file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import contextlib
import difflib
import re
import sys

import utila


def forward_slash(content: str, newline: bool = False) -> str:
    r"""Replace every backward slash \\ with an forward slash /.

    Args:
        content(str): content with backslash's
        newline(bool): if True, do not convert \n to /n
    Returns:
        content without backslash's

    Examples:
    >>> forward_slash('\\helm\nelm', newline=True)
    '/helm\nelm'
    >>> forward_slash('\\helm\\telm', newline=True)
    '/helm/telm'
    >>> forward_slash('\\helm\\nelm')
    '/helm/nelm'
    """
    pattern = r'\\'
    if newline:
        pattern = r'\\(?!n)'
    content = re.sub(re.compile(pattern), '/', content)
    return content


def fix_encoding(msg: str) -> str:
    """Remove invalid character to display on console

    Args:
        msg(str): message with invalid character
    Returns:
        message `without` invalid character
    """
    # ensure to have str
    msg = str(msg)
    # convert for windows console
    encoding = 'cp1252' if sys.platform in ('win32', 'cygwin') else 'utf-8'
    # remove non valid char to avoid errors on win-console
    msg = msg.encode(encoding, errors='xmlcharrefreplace').decode(encoding)
    return msg


def normalize_whitespaces(text: str) -> str:
    r"""Remove unnecessary white spaces.

    >>> normalize_whitespaces(' make    me happy' + '\n')
    'make me happy'
    """
    return ' '.join(text.strip().split())


def normalize_text(
    items,
    *,
    merge_divis: bool = True,
    normalize_newline: bool = True,
    normalize_spaces: bool = False,
) -> str:
    r"""\
    >>> normalize_text(['Dieser Satz ent-\n', 'hält eine Trennung.'], merge_divis=True)
    'Dieser Satz enthält eine Trennung.'
    >>> normalize_text(['Der Stadtteil Berlin-\n', 'Neuköln liegt im Süden von Berlin.'])
    'Der Stadtteil Berlin-Neuköln liegt im Süden von Berlin.'
    >>> normalize_text('Das  sind   eindeutig zu   viele Trennungen.', normalize_spaces=True)
    'Das sind eindeutig zu viele Trennungen.'
    >>> normalize_text(['Special Char' + chr(173) + '\n', 'sol hier'])
    'Special Charsol hier'
    >>> normalize_text([''])
    ''
    """
    # prepare input data
    with contextlib.suppress(AttributeError, TypeError):
        items = [item.text for item in items]
    text = ''.join(items)
    if merge_divis:
        # Ensure that divis of following UpperCase-Word is not merged
        # TODO: IMPORVE REGEX
        text = re.sub(r'[-\xad]\n(?P<data>[a-zäöü])', r'\g<data>', text)
        text = re.sub(r'[-\xad]\n(?P<data>[A-ZÄÖÜ])', r'-\g<data>', text)
    if normalize_newline:
        text = text.replace('\n', ' ')
    if normalize_spaces:
        text = re.sub(r'\s+', ' ', text)
    return text


def simplify_chars(
    text: str,
    *,
    table: bool = False,
) -> str:
    """\
    >>> simplify_chars('Überschrift Φ', table=True)
    'UEberschrift PH'
    """
    # TODO: EXTEND
    text = text.replace('–', '-')
    if table:
        text = utila.replace(text)
    return text


def istemplate_replaced(text: str):
    """Check if some pattern `{% %}` is not replaced.

    >>> istemplate_replaced('hello')
    True
    >>> istemplate_replaced('%}')
    False
    """
    if '{%' in text:
        return False
    if '%}' in text:
        return False
    return True


def shrink(content: str, maxlength: int = 300) -> str:
    """\
    >>> shrink('abcdefg', maxlength=6)
    'abc[...]efg'
    >>> shrink(b'bytesbytesbytes', maxlength=10)
    'bytes[...]bytes'
    >>> shrink('abcdefg')
    'abcdefg'

    without converting list to str, this example would produce a long
    string, cause max length will check against list length:
    >>> shrink(['a'*1000]*5, 6)
    "['a[...]a']"
    """
    assert maxlength >= 0, str(maxlength)
    if isinstance(content, bytes):
        content = content.decode('utf8', errors='replace')
    else:
        # convert list, int etc. to str
        content = str(content)
    if len(content) <= maxlength:
        return content
    half = int(maxlength / 2)
    before = content[0:half]
    after = content[-half:]
    result = f'{before}[...]{after}'
    return result


# Hint: Do not add string
ITERABLE = (list, tuple, set)


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
    """
    # TODO: SWITCH EXPECTED AND CURRENT PARAMETER AND INCREASE MAJOR VERSION
    if not isinstance(expected, ITERABLE):
        expected = [expected]
    expected = utila.strip(*expected)
    expected = utila.lower(*expected)
    if isinstance(current, ITERABLE):
        for item in current:
            if similar(expected=expected, current=item, maxdiff=maxdiff):
                return True
        return False
    matched = difflib.get_close_matches(
        word=current.strip().lower(),
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
    """
    if len(expected) <= 4:
        return similar(current=current, expected=expected, maxdiff=0.80)
    return similar(current=current, expected=expected, maxdiff=0.9)


def inside(current: str, expected: str, maxdiff: float = 0.1) -> bool:
    """\
    >>> inside('Helmut', 'Der Helmut wohnt in Berlin')
    True
    >>> inside('Helmut', ['Der Helm wohnt in Berlin'], maxdiff=0.3)
    True
    >>> inside('1. FC Union Berlin', 'An der alten Försterei spielt Union Berlin', maxdiff=0.3)
    True
    """
    current = current.lower()
    if isinstance(expected, (list, tuple)):
        # multiple expected options
        return any((inside(current, item, maxdiff) for item in expected))
    expected = expected.lower()
    if current in expected:
        return True
    curlen = len(current)
    # TODO: SLOW APPROACH
    # DIRTY
    for side in range(curlen):
        splitted = [
            expected[index * curlen + side:side + (index + 1) * curlen]
            for index in range(int(len(expected) / curlen) + 1)
        ]
        if similar(current, splitted, maxdiff=maxdiff):
            return True
    return False


def lower(*items):
    """Lowercase list of strings.

    >>> lower('Helmut', 'MANFRED')
    ['helmut', 'manfred']
    """
    return [item.lower() for item in items]


def strip(*items):
    """Strip list of strings.

    >>> strip(' Helmut  ', ' MANFRED')
    ['Helmut', 'MANFRED']
    """
    return [item.strip() for item in items]


def splitlines(raw: str, lowers: bool = True) -> set:
    r"""Split string by newlines and convert to set.

    >>> splitlines('First\nThird\nSecond')
    {'third', 'second', 'first'}
    """
    raw = raw.strip()
    if lowers:
        raw = raw.lower()
    splitted = raw.strip().splitlines()
    return set(splitted)


def splititems(raw: str, lowers: bool = True) -> set:
    r"""Split string by whitespace and convert to set.

    >>> splititems('First   Third\nSecond')
    {'third', 'second', 'first'}
    """
    raw = raw.strip()
    if lowers:
        raw = raw.lower()
    raw = normalize_text(
        raw,
        merge_divis=False,
        normalize_spaces=True,
        normalize_newline=True,
    )
    splitted = raw.split()
    return set(splitted)


ALPHA = 'abcdefghijklmnopqrstuvwxyzäöüß '


def char_rate(text: str) -> float:
    """\
    >>> char_rate('AB12DF')
    0.67
    """
    if not text:
        return 0.0
    text = text.lower()
    selected = len([item for item in text if item in ALPHA])
    rate = selected / len(text)
    return utila.roundme(rate)


def findindex(text: str, token: str) -> list:
    """\
    >>> findindex('Hier spricht Dr. Helmut Der 1. PrÃ¤sident von spricht.', token='.')
    [15, 29, 53]
    >>> findindex('Hier spricht Dr. Helmut Der 1. PrÃ¤sident von spricht.', token='Hier')
    [0]
    >>> findindex('Hier spricht Dr. Helmut Der 1. PrÃ¤sident von spricht.', token='empty')
    []
    """
    result = []
    index = -1
    while True:
        index = text.find(token, index + 1)
        if index == -1:
            break
        result.append(index)
    return result


def findindexs(text: str, tokens: tuple) -> list:
    """\
    >>> findindexs('ABCDEFGAHCABCDEFGAHC', ('A', 'DE'))
    [0, 3, 7, 10, 13, 17]
    """
    assert len(tokens) == len(set(tokens)), f'duplicated tokes: {tokens}'
    result = []
    for token in tokens:
        result.extend(findindex(text, token))
    result.sort()
    return result
