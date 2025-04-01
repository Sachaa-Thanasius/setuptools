"""Text-related functions adapted from jaraco.text 3.12.1."""

from __future__ import annotations

import functools
import itertools
from collections.abc import Iterable
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

_NestedStr: TypeAlias = Union[str, Iterable[Union[str, Iterable["_NestedStr"]]]]


def _nonblank(str: str):
    return str and not str.startswith('#')


@functools.singledispatch
def yield_lines(iterable: _NestedStr) -> itertools.chain[str]:
    r"""
    Yield valid lines of a string or iterable.

    >>> list(yield_lines(''))
    []
    >>> list(yield_lines(['foo', 'bar']))
    ['foo', 'bar']
    >>> list(yield_lines('foo\nbar'))
    ['foo', 'bar']
    >>> list(yield_lines('\nfoo\n#bar\nbaz #comment'))
    ['foo', 'baz #comment']
    >>> list(yield_lines(['foo\nbar', 'baz', 'bing\n\n\n']))
    ['foo', 'bar', 'baz', 'bing']
    """
    return itertools.chain.from_iterable(map(yield_lines, iterable))


@yield_lines.register(str)
def _(text: str) -> filter[str]:
    return filter(_nonblank, map(str.strip, text.splitlines()))


def drop_comment(line: str) -> str:
    """
    Drop comments.

    >>> drop_comment('foo # bar')
    'foo'

    A hash without a space may be in a URL.

    >>> drop_comment('http://example.com/foo#bar')
    'http://example.com/foo#bar'
    """
    return line.partition(' #')[0]


def join_continuation(lines):
    r"""
    Join lines continued by a trailing backslash.

    >>> list(join_continuation(['foo \\', 'bar', 'baz']))
    ['foobar', 'baz']
    >>> list(join_continuation(['foo \\', 'bar', 'baz']))
    ['foobar', 'baz']
    >>> list(join_continuation(['foo \\', 'bar \\', 'baz']))
    ['foobarbaz']
    >>> list(join_continuation(['goo\\', 'dly']))
    ['goodly']

    A terrible idea, but...
    If no line is available to continue, suppress the lines.

    >>> list(join_continuation(['foo', 'bar\\', 'baz\\']))
    ['foo']
    """
    lines = iter(lines)
    for item in lines:
        while item.endswith('\\'):
            try:
                item = item[:-1].strip() + next(lines)
            except StopIteration:
                return
        yield item
