class App(object):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

class Fmap(App):
    pass

class Bind(App):
    pass

# Term representing failure of a computation

class Fail(object):
    def __init__(self, fail_env):
        self.env = fail_env

# TODO: Terms representing functional abstraction and fixpoint

#class Lam(object):
#    def __init__(self, func):
#        self.func = func

#class Fix(object):
#    def __init__(self, func):
#        self.func = func

# TODO: Term representing variable _introduction_

# class Var(object):
#    def __init__(self, val):
#        self.val = val


