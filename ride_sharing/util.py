def compose(*args):
    def composed(val):
        for arg in reversed(args):
            val = arg(val)
        return val
    return composed
