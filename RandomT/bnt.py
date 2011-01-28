from inference import InferenceEngine

from bntops import *

from matlabexec import run_matlab_script
from matlabexec import read_matlab_array

class BNTEngine(InferenceEngine):
	def __init__(self, expr, impl_type='jtree_inf_engine'):
		InferenceEngine.__init__(self, expr)
		self.impl_type = impl_type
	
	def marginalize(self, var, evidence={}):
		# Compile the BNet spec
		self.script, self.ordered_domains, self.var_ids = lazynet_to_bnt_spec(self.expr)
		self.script += init_inference_engine(self.impl_type)
		
		# if there is evidence, specify it
		if len(evidence) != 0:
			for (k, v) in evidence.items():
				self.script += observe_evidence(self.var_ids[k], self.ordered_domains[k][v])
		
		self.script += marginalize(self.var_ids[var])
		
		# Compile output routine
		self.script += output_marginalize()
		
		# Put in a quit.
		self.script += "quit\n"
		
#		print "Running script"
		# Run the script.
		run_matlab_script(self.script)
		
		# Read the results.
#		print "Finished. Reading result"
		result = read_matlab_array("marg.mat")
		var_dom_dict = self.ordered_domains[var]
		
		output = {}
		for i in range(len(result)):
			ordered_to_normal = dict([(y, x) for (x, y) in var_dom_dict.items()])
			output[ordered_to_normal[i]] = result[i]
		
		return output
