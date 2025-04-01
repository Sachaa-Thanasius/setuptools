from __future__ import annotations

import sys
import types
from collections.abc import Callable, Iterable, Iterator
from typing import Any, TypeVar

# The type of isinstance's second argument (from typeshed builtins)
if sys.version_info >= (3, 10):
    _ClassInfo = type | types.UnionType | tuple["_ClassInfo", ...]
else:
    _ClassInfo = type | tuple[_ClassInfo, ...]

_T = TypeVar("_T")
_U = TypeVar("_U")


# copied from jaraco.itertools 6.1
def ensure_unique(iterable, key=lambda x: x):
    """
    Wrap an iterable to raise a ValueError if non-unique values are encountered.

    >>> list(ensure_unique('abc'))
    ['a', 'b', 'c']
    >>> list(ensure_unique('abca'))
    Traceback (most recent call last):
    ...
    ValueError: Duplicate element 'a' encountered.
    """
    seen = set()
    seen_add = seen.add
    for element in iterable:
        k = key(element)
        if k in seen:
            raise ValueError(f"Duplicate element {element!r} encountered.")
        seen_add(k)
        yield element


# copied from more-itertools 10.6.0
def always_iterable(
    obj: object,
    base_type: _ClassInfo | None = (str, bytes),
) -> Iterator[Any]:
    """If *obj* is iterable, return an iterator over its items::

        >>> obj = (1, 2, 3)
        >>> list(always_iterable(obj))
        [1, 2, 3]

    If *obj* is not iterable, return a one-item iterable containing *obj*::

        >>> obj = 1
        >>> list(always_iterable(obj))
        [1]

    If *obj* is ``None``, return an empty iterable:

        >>> obj = None
        >>> list(always_iterable(None))
        []

    By default, binary and text strings are not considered iterable::

        >>> obj = 'foo'
        >>> list(always_iterable(obj))
        ['foo']

    If *base_type* is set, objects for which ``isinstance(obj, base_type)``
    returns ``True`` won't be considered iterable.

        >>> obj = {'a': 1}
        >>> list(always_iterable(obj))  # Iterate over the dict's keys
        ['a']
        >>> list(always_iterable(obj, base_type=dict))  # Treat dicts as a unit
        [{'a': 1}]

    Set *base_type* to ``None`` to avoid any special handling and treat objects
    Python considers iterable as iterable:

        >>> obj = 'foo'
        >>> list(always_iterable(obj, base_type=None))
        ['f', 'o', 'o']
    """
    if obj is None:
        return iter(())

    if (base_type is not None) and isinstance(obj, base_type):
        return iter((obj,))

    try:
        return iter(obj)  # type: ignore [call-overload]
    except TypeError:
        return iter((obj,))


# copied from more-itertools 10.6.0
def unique_everseen(
    iterable: Iterable[_T],
    key: Callable[[_T], _U] | None = None,
) -> Iterator[_T]:
    """
    Yield unique elements, preserving order.

        >>> list(unique_everseen('AAAABBBCCDAABBB'))
        ['A', 'B', 'C', 'D']
        >>> list(unique_everseen('ABBCcAD', str.lower))
        ['A', 'B', 'C', 'D']

    Sequences with a mix of hashable and unhashable items can be used.
    The function will be slower (i.e., `O(n^2)`) for unhashable items.

    Remember that ``list`` objects are unhashable - you can use the *key*
    parameter to transform the list to a tuple (which is hashable) to
    avoid a slowdown.

        >>> iterable = ([1, 2], [2, 3], [1, 2])
        >>> list(unique_everseen(iterable))  # Slow
        [[1, 2], [2, 3]]
        >>> list(unique_everseen(iterable, key=tuple))  # Faster
        [[1, 2], [2, 3]]

    Similarly, you may want to convert unhashable ``set`` objects with
    ``key=frozenset``. For ``dict`` objects,
    ``key=lambda x: frozenset(x.items())`` can be used.

    """
    seenset: set[_T | _U] = set()
    seenset_add = seenset.add
    seenlist: list[_T | _U] = []
    seenlist_add = seenlist.append
    use_key = key is not None

    for element in iterable:
        k = key(element) if use_key else element  # type: ignore [misc]
        try:
            if k not in seenset:
                seenset_add(k)
                yield element
        except TypeError:
            if k not in seenlist:
                seenlist_add(k)
                yield element
