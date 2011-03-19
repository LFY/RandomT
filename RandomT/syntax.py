from util import *

class DerivedExpr(object):
    def __init__(self, expr):
        self.expr = expr

evalDExpr = lambda de: de.expr

def mk_class_with_interface(some_class, interp, ast_type):
    def make_abstract(method):
        def abstract_method_call(self, *args):
            other_exprs = map(lambda e: e.expr, args)
            app_node = ast_type(method, self.expr, *other_exprs)
            result = interp(app_node) # Fully evaluate to figure out the class to imitate
            return mk_class_with_interface(type(result), interp, ast_type)(app_node)
        return abstract_method_call

    methods_only = filterdv(
            lambda f: type(f) in [
                type(make_abstract),
                type(lambda : 1), 
                type(int.__add__), 
                type(list.insert)],
            some_class.__dict__)

    no_meta = filterdk(
            lambda n: n not in [
                '__getattribute__',
                '__getformat__',
                '__repr__',
                '__str__'],
            methods_only)

    transformed = mapdv(make_abstract, no_meta)

    newclass = type('Abstract_%s' % some_class.__name__, (DerivedExpr,), transformed)

    # Need to override base class's __hash__ so all the sharing stuff is based on object reference equality not extensional equality
    newclass.__hash__ = lambda self: id(self)

    # Sadly, Python forces __hash__ and __eq__ to return consistent values,
    # so we need to override the base class __eq__ and __neq__ methods 
    # to compare object reference equality;
    # we can't use the base class extensional __eq__, __neq__
    newclass.__eq__ = lambda self, other: id(self) == id(other)
    newclass.__ne__ = lambda self, other: id(self) != id(other)
    return newclass

