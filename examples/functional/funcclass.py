
def stub():
	pass

def isFunction(f):
	return type(f) in (type(lambda: 1), type(int.__add__), type(stub))

class Function(object):
	def __init__(self, f):
		if isFunction(f):
			self.func = f
		elif type(f) is type(self):
			self.func = f.func
		
	def __call__(self, *args, **kwargs):
		rtval = self.func(*args, **kwargs)
		# Infect.
		if isFunction(rtval):
			return Function(rtval)
		else:
			return rtval

