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

# Term representing functional abstraction

#class Lam(object):
#    def __init__(self, func):
#        self.func = func
