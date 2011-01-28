import os

def run_matlab_script(scr):
	script_name = "current"
	fh = open(script_name + ".m", 'w')
	fh.write(scr)
	fh.close()
	
	cmd = "matlab -r " + script_name + " -nodisplay -nosplash > matlogfile"
	os.system(cmd)

def read_matlab_array(filename):
	fh = open(filename, 'r')
	s = map(lambda x: float(x), fh.readlines())
	fh.close()
	
	return s

#run_matlab_script("x = 0; y = 1; README = [x y]'\nquit\n")
#print read_matlab_array('output.mat')
