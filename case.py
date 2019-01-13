class _CaseMatching:
    def __init__(self, obj):
        self.pt = []
        self.obj = obj
        pass

    def __or__(self, case):
        self.pt.append(case)
        return self

    def end(self):
        for case in self.pt:
            if isinstance(case.check, FunctionType) and case.check():
                return case.result()
            if (
                self.obj is not None
                and inspect.isclass(case.check)
                and isinstance(self.obj, case.check)
            ):
                var_lst = case.result.__code__.co_varnames
                return case.result(**{k: getattr(self.obj, k) for k in var_lst})
            if self.obj is not None and self.obj == case.check:
                return case.result()
        raise Exception()


class case:
    def __init__(self, check):
        self.check = check

    def __rshift__(self, result):
        self.result = result
        return self


def when(objOrf, f=None):
    if f is not None:
        a = _CaseMatching(objOrf)
    else:
        a = _CaseMatching(None)
        f = objOrf
    f(a)
    return a.end()


def value(v):
    return lambda: v


otherwise = case(lambda: True)
