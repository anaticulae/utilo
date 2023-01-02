# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2019-2023 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import binascii
import contextlib
import difflib
import functools
import re
import statistics
import sys
import warnings

import utila

BACKSLASH = re.compile(r'\\')
NEWLINE = re.compile(r'\\(?!n)')


def forward_slash(content: str, keep_newline: bool = False, **kwargs) -> str:  # pylint:disable=W9015
    r"""Replace every backward slash \\ with an forward slash /.

    Args:
        content(str): content with backslash's
        keep_newline(bool): if True, do not convert \n to /n
    Returns:
        content without backslash's

    Examples:
    >>> forward_slash('\\helm\nelm', keep_newline=True)
    '/helm\nelm'
    >>> forward_slash('\\helm\\telm', keep_newline=True)
    '/helm/telm'
    >>> forward_slash('\\helm\\nelm')
    '/helm/nelm'
    """
    assert isinstance(content, str), str(content)
    pattern = BACKSLASH
    if 'newline' in kwargs:
        keep_newline = kwargs['newline']
        warnings.warn("replace with keep_newline", DeprecationWarning)
    if keep_newline:
        pattern = NEWLINE
    content = re.sub(pattern, '/', content)
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
    encoding = 'cp1252' if 'win' in sys.platform else 'utf-8'
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
    strips: bool = False,
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
    >>> normalize_text(' Strip ?  ', strips=True)
    'Strip ?'
    >>> normalize_text('A B    C\nD E    F\n G H', normalize_newline=False, normalize_spaces=True)
    'A B C\nD E F\n G H'
    >>> normalize_text('A B    C\nD E    F\n G H', normalize_spaces=True)
    'A B C D E F G H'
    """
    text = text_prepare(items)
    if merge_divis:
        # Ensure that divis of following UpperCase-Word is not merged
        # TODO: IMPORVE REGEX
        text = re.sub(r'[-\xad]\n(?P<data>[a-zäöü])', r'\g<data>', text)
        text = re.sub(r'[-\xad]\n(?P<data>[A-ZÄÖÜ])', r'-\g<data>', text)
    if normalize_newline:
        text = text.replace('\n', ' ')
    if normalize_spaces:
        text = re.sub(r'[ ]+', ' ', text)
    if strips:
        text = text.strip()
    return text


def text_prepare(items: str) -> str:
    if isinstance(items, str):
        return items
    with contextlib.suppress(AttributeError, TypeError):
        items = [item.text for item in items]
    if utila.iterable(items) and len(items) > 1:
        items = [(item + ' ' if item[-1] not in '\n ' else item)
                 for item in items[:-1]] + [items[-1]]
    result = ''.join(items)
    return result


def final_newline(text: str) -> str:
    r"""Ensure valid unix final with a ending final newline.

    >>> final_newline('hello')
    'hello\n'
    """
    return text.rstrip() + utila.NEWLINE


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
    if isinstance(content, bytes):  # pylint:disable=W0160
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
        if utila.similar(current, splitted, maxdiff=maxdiff):
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


def nowhitespace(*items):
    """Remove whitespaces inside list of strings.

    >>> nowhitespace(' A B S T R A C T  ',)
    ['ABSTRACT']
    """
    return [item.replace(' ', '') for item in items]


REGEX_NEWLINE = re.compile('\n+')


def splitlines(
    raw: str,
    lowers: bool = True,
    pattern: str = REGEX_NEWLINE,
    unique: bool = True,
    unique_assert: bool = False,
) -> set:
    r"""Split string by newlines and convert to set.

    >>> splitlines('First\nThird\nSecond')
    {'third', 'second', 'first'}
    >>> splitlines('First\nThird\n\n\n')
    {'third', 'first'}
    """
    if lowers:
        raw = raw.lower()
    if pattern != REGEX_NEWLINE:
        pattern = re.compile(pattern)
    splitted = pattern.split(raw)
    splitted = utila.notempty(splitted)
    assert not unique_assert or len(set(splitted)) == len(splitted)
    result = set(splitted) if unique else splitted
    return result


splitdouble = functools.partial(splitlines, pattern=re.compile(r'\n\n'))


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


def char_rate(text: str, special: str = None) -> float:
    """\
    >>> char_rate('AB12DF')
    0.67
    >>> char_rate('AB12DF', special='12')
    1.0
    """
    if not text:
        return 0.0
    text = text.lower()
    valid = ALPHA
    if special:
        valid = valid + special
    selected = len([item for item in text if item in valid])
    rate = selected / len(text)
    return utila.roundme(rate)


def findindex(text: str, token: str, count=None) -> list:
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
    while True:  # pylint:disable=W0149
        index = text.find(token, index + 1)
        if index == -1:
            break
        result.append(index)
    if count == 1:
        return result[0] if result else None
    return result


def findindexs(text: str, tokens: tuple) -> list:
    """\
    >>> findindexs('ABCDEFGAHCABCDEFGAHC', ('A', 'DE'))
    [0, 3, 7, 10, 13, 17]
    >>> findindexs('super seite: https://checkitweg.de', tokens='http https'.split())
    [13]
    """
    assert len(tokens) == len(set(tokens)), f'duplicated tokes: {tokens}'
    result = []
    for token in tokens:
        result.extend(findindex(text, token))
    # TODO: SHRINK PATTERN INSTEAD OF SHRINKING CONTENT, TO AVOID DUPLICATION
    result = utila.make_unique(result)
    result.sort()
    return result


def rreplace(content: str, pattern: str, replace: str, count: int = 1):
    """\
    >>> rreplace('/test_figures_run_bachelor56page270/'
    ... 'figureo__standard_figures/62711c57d36', 'figureo__standard_figures', 'repl')
    '/test_figures_run_bachelor56page270/repl/62711c57d36'
    """
    while count > 0:  # pylint:disable=W0149
        index = content.rfind(pattern)
        if index == -1:
            break
        rend = index + len(pattern)
        content = content[:index] + replace + content[rend:]
        count = count - 1
    return content


SIMPLIFY = str.maketrans({item: '' for item in ' _-=+,.;\'/"()!@#$%^&&*'})


def simple(item: str, maxlength: int = 25) -> str:
    """Simplify test name to ease selecting generated tests by test name.

    >>> simple('No spaces _+; 133')
    'Nospaces133'
    """
    item = utila.fix_encoding(item)
    item = item.translate(SIMPLIFY)
    item = item[-maxlength:]
    return item


def binhash(data: bytes) -> int:
    """\
    >>> binhash(b'hello')
    907060870
    """
    result = binascii.crc32(data)
    return result


def assert_bin(data: bytes, expected: int):
    current = binhash(data)
    assert current == expected, f'{current}=={expected}'


INT_START = re.compile(r'^\d{1,3}[^\.,]')


def starts_withint(text: str) -> bool:
    """\
    >>> starts_withint('1 First Line')
    True
    >>> starts_withint('2.0 No Float start')
    False
    """
    text = text.strip()
    if INT_START.search(text):
        return True
    return False


def starts_with(line: str, start: str) -> bool:
    """\
    >>> starts_with('Methode3', '2 Methode3')
    True
    >>> starts_with(line='5.1.2.  Einzelne  Aktionspunkte  des  OECD-BEPS-Projekts'
    ... '  und  den  korrespondierenden Maßnahmen auf EU-Ebene',
    ... start='5.1.2.  Einzelne  Aktionspunkte  des  OECD-BEPS-Projekts  '
    ... 'und  den  korrespondierenden')
    True
    """
    # shrink line to start pattern to match if line is much longer than
    # start pattern.
    line = line[0:len(start)]
    start = start[0:len(line)]  # TODO: REMOVE THIS?
    maxdiff = 0.9 if len(start) > 10 else 0.7  # TODO: HOLY VALUE
    if utila.similar(start, line, maxdiff=maxdiff):
        return True
    return False


def dict_dump(data, keywidth: int = 20) -> str:
    r"""\
    >>> dict_dump(dict(hello=10, data='Hier spricht Helm'))
    'hello               10\ndata                Hier spricht Helm'
    """
    line = '{:<' + str(keywidth) + '}{}'
    collected = []
    for key, value in data.items():
        collected.append(line.format(key, value))
    result = utila.NEWLINE.join(collected)
    return result


@utila.cacheme
def issinglechar(text: str) -> bool:
    """\
    >>> issinglechar('A B S T R A C T')
    True
    >>> issinglechar('  ')
    False
    >>> issinglechar('2 background 9')
    False
    >>> issinglechar('M U LT I - S O U R C E D E T E C T A N O M A L I E S')
    True
    """
    if not text:
        return False
    splitted = [len(token) for token in text.strip().split()]
    if not splitted:
        return False
    mean = statistics.mean(splitted)
    if 1.0 <= mean < 1.15:
        return True
    return False
