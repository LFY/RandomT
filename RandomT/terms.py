class App(object):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

class Fmap(App):
    pass

class Bind(App):
    pass

