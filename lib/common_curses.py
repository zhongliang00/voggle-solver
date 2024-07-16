import json
import re
from collections import Counter
from typing import Callable

from forbiddenfruit import curse as _curse


# from tqdm.autonotebook import tqdm as _tqdm
# from dev_utils.date_utils import to_date
# tqdm = partial(_tqdm, delay=2)

def not_impl(*args, **kwargs):
    raise NotImplementedError


to_date = not_impl
tqdm = not_impl

_sentinel = object()


# support curse multiple classes at once
def mcurse(cls, func):
    if not isinstance(func, list):
        func = [func]

    names_funcs = []
    for f in func:
        if isinstance(f, tuple):
            names_funcs.append(f)
        else:
            names_funcs.append((f.__name__.rsplit('_', maxsplit=1)[-1], f))

    if not isinstance(cls, list):
        cls = [cls]

    for c in cls:
        for name, f in names_funcs:
            _curse(c, name, f)


#
# string curses
#


def str_len(self):
    return len(self)


def str_json(self, fallback=_sentinel):
    if fallback is _sentinel:
        return json.loads(self)
    else:
        from json import JSONDecodeError
        try:
            return json.loads(self)
        except JSONDecodeError as e:
            return fallback


def str_date(self):
    return to_date(self)


def str_match(self, s):
    match = re.compile(s, re.IGNORECASE)
    return bool(re.search(match, self))


def str_nmatch(self, s):
    return not self.match(s)


def str_grep(self, s):
    match = re.compile(s, re.IGNORECASE)
    match_obj = re.search(match, self)
    return None if match_obj is None else match_obj[0]


def str_print(self):
    print(self)


mcurse(str, [str_len, str_json, str_date, str_match, str_nmatch, str_grep, str_print])


#
# collection curses
#

def s2callable(s):
    if callable(s):
        return s
    match = re.compile(s, re.IGNORECASE)
    return lambda _: bool(re.search(match, str(_)))


def verbose_op(self, op_name: str, *args, **kwargs):
    before = len(self)
    out = self.__getattribute__(op_name)(*args, **kwargs)
    after = len(out)

    if 'progress' in kwargs:
        del kwargs['progress']

    description = [op_name]
    if len(args) > 0:
        description.append(f"'{args}'")
    if len(kwargs) > 0:
        description.append(f"'{kwargs}'")
    description = ' '.join(description)

    print(f"---------- {description} (removed {before - after})")
    print(f"Left {after}\t")
    return out


def generic_len(self):
    return len(self)


def generic_iter(self, reverse=False, progress=False):
    from collections.abc import Mapping
    if isinstance(self, Mapping):
        iterable = self.items()
    else:
        iterable = self
    if reverse:
        iterable = reversed(iterable)
    if progress:
        iterable = tqdm(iterable, total=len(self))
    return iter(iterable)


def generic_map(self, s: Callable, progress=False):
    return self.__class__(s(_) for _ in self.iter(progress=progress))


def generic_get(self, idx, default_value=None):
    try:
        return self[idx]
    except IndexError:
        return default_value


def generic_first(self, default_value=None):
    try:
        return next(self.iter())
    except StopIteration:
        return default_value


def generic_last(self, default_value=None):
    try:
        return next(self.iter(reverse=True))
    except StopIteration:
        return default_value


def generic_filter(self, s: Callable, progress=False):
    return self.__class__(_ for _ in self.iter(progress=progress) if s(_))


def generic_nfilter(self, s: Callable, progress=False):
    return self.__class__(_ for _ in self.iter(progress=progress) if not s(_))


def generic_vfilter(self, s: Callable, progress=False):
    return verbose_op(self, 'filter', s, progress=progress)


def generic_vnfilter(self, s: Callable, progress=False):
    return verbose_op(self, 'nfilter', s, progress=progress)


def generic_sorted(self, key=lambda _: _):
    return self.__class__(sorted(self.iter(), key=key))


def generic_cast(self, cls):
    return cls(self.iter())


def generic_tolist(self):
    return list(self.iter())


def generic_enumerate(self, start=0):
    from collections.abc import Sequence
    cls = self.__class__ if isinstance(self, Sequence) else list
    return cls(enumerate(self.iter(), start=start))


def generic_grep(self, s, progress=False):
    return self.filter(s2callable(s), progress=progress)


def generic_ngrep(self, s, progress=False):
    return self.nfilter(s2callable(s), progress=progress)


def generic_join(self, sep=''):
    return sep.join(self.iter())


mcurse([tuple, list, set], [generic_get, generic_join])
mcurse(
    [tuple, list, set, dict],
    [
        generic_len, generic_iter, generic_map,
        generic_first, generic_last,
        generic_filter, generic_nfilter, generic_vfilter, generic_vnfilter, generic_sorted,
        generic_cast, generic_tolist,
        generic_enumerate, generic_grep, generic_ngrep
    ]
)
mcurse([type({}.keys()), type({}.values()), type({}.items())], [
    generic_iter, generic_cast, generic_tolist
])
mcurse(str, [generic_iter, generic_cast])


def list_flatten(self, progress=False):
    return self.__class__(item for sublist in self.iter(progress=progress) for item in sublist)


def list_drop(self, s: Callable, progress=False):
    idxs = [i for i, c in enumerate(self.iter(progress=progress)) if s(c)]
    for i in reversed(idxs):
        self.pop(i)
    return self


def list_keep(self, s: Callable, progress=False):
    return self.drop(lambda _: not s(_), progress=progress)


def list_counter(self):
    return Counter(self)


def list_groupby(self, key=lambda _: _, progress=False):
    d = {}
    for item in self.iter(progress=progress):
        k = key(item)
        if k not in d:
            d[k] = self.__class__()
        d[k].append(item)
    return d


def list_unique(self, key=lambda _: _, reduce=lambda _: _[0], progress=False):
    d = self.groupby(key, progress=progress)
    return self.__class__(reduce(v) for v in d.values())


def list_zip(self, *others):
    cs = self.__class__
    return cs(zip(self, *others))


def list_product(self, *others):
    from itertools import product
    cs = self.__class__
    return cs(product(self, *others))


mcurse(list, [
    list_flatten, list_drop, list_keep,
    list_counter, list_groupby, list_unique, list_zip, list_product,
])


def dict_drop(self, s: Callable, progress=False):
    keys = [k for k, v in self.iter(progress=progress) if s(k, v)]
    for k in keys:
        del self[k]
    return self


def dict_keep(self, s: Callable, progress=False):
    return self.drop(lambda k, v: not s(k, v), progress=progress)


def dict_outer(self, *others):
    ds = [self] + list(others)
    all_keys = {}
    for d in ds:
        for k in d.keys():
            all_keys[k] = []
    for d in ds:
        for k, v in all_keys.items():
            v.append(d.get(k, None))
    for k, v in all_keys.items():
        all_keys[k] = tuple(v)
    return self.__class__(all_keys)


def dict_inner(self, *others):
    ds = [self] + list(others)
    all_keys = {}
    for d in ds:
        for k in d.keys():
            all_keys[k] = []
    for k, v in all_keys.items():
        if not all(k in d for d in ds):
            continue
        v.extend([d[k] for d in ds])
    for k, v in all_keys.items():
        all_keys[k] = tuple(v)
    return self.__class__(all_keys)


def dict_join(self, *others):
    return self.outer(*others)


def dict_sortv(self, key=lambda _: _):
    return self.__class__(sorted(self.items(), key=lambda _: key(_[1])))


def dict_mapk(self, s: Callable, overwrite_keys=False, progress=False):
    out = {}
    for k, v in self.iter(progress=progress):
        nk = s(k)
        if nk in out and not overwrite_keys:
            raise ValueError(f"Key {nk} already exists (overwrite_keys=False) (mapped from {k})")
        else:
            out[nk] = v
    return self.__class__(out)


def dict_mapv(self, s: Callable, progress=False):
    return self.__class__((k, s(v)) for k, v in self.iter(progress=progress))


def dict_bj(self):
    return len(self.keys()) == len(set(self.values()))


def dict_reverse(self):
    if not self.bj():
        raise ValueError("Not a bijection")
    return self.__class__((v, k) for k, v in self.items())


def dict_grepk(self, s, progress=False):
    return self.filter(lambda kv: s2callable(s)(kv[0]), progress=progress)


mcurse(dict, [
    dict_drop, dict_keep, dict_sortv,
    dict_outer, dict_inner, dict_join,
    dict_mapk, dict_mapv,
    dict_bj, dict_reverse,
    dict_grepk
])


def counter_pct(self):
    d = dict(self)
    n = sum(d.values())
    return {k: v / n for k, v in d.items()}


mcurse(Counter, [counter_pct])
