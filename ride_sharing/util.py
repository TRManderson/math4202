def tails(ls):
    src = ls.copy()
    while len(src):
        yield src
        src = src.copy()
        src.pop()

def tail(iterable):
    i = iter(iterable)
    next(i)
    yield from i
